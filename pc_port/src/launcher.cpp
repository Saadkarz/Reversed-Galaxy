#include "launcher.hpp"

#include "dol.hpp"
#include "sha1.hpp"

#include <system_error>
#include <vector>

namespace fs = std::filesystem;

namespace g2c {

std::string sha1_of_file(const fs::path& path) {
    std::vector<u8> bytes;
    if (!read_file(path.string(), bytes)) {
        return {};
    }
    return sha1_hex(bytes.data(), bytes.size());
}

GameDataImporter::GameDataImporter(fs::path gameDataDir) : mGameDataDir(std::move(gameDataDir)) {}

GameDataImporter::~GameDataImporter() {
    if (mWorker.joinable()) {
        mWorker.join();
    }
}

bool GameDataImporter::hasValidGameData() const {
    const fs::path dol = mGameDataDir / "sys" / "main.dol";
    std::error_code ec;
    return fs::is_regular_file(dol, ec) && sha1_of_file(dol) == kExpectedDolSha1;
}

void GameDataImporter::start(const fs::path& extractedRoot) {
    if (mState == State::Verifying || mState == State::Copying) {
        return;
    }
    if (mWorker.joinable()) {
        mWorker.join();
    }
    mDone = 0;
    mTotal = 0;
    mState = State::Verifying;
    {
        std::lock_guard<std::mutex> g(mMsgLock);
        mMessage = "Verifying main.dol...";
    }
    mWorker = std::thread(&GameDataImporter::run, this, extractedRoot);
}

float GameDataImporter::progress() const {
    const auto total = mTotal.load();
    return total ? static_cast<float>(mDone.load()) / static_cast<float>(total) : 0.0f;
}

std::string GameDataImporter::message() const {
    std::lock_guard<std::mutex> g(mMsgLock);
    return mMessage;
}

void GameDataImporter::fail(const std::string& msg) {
    {
        std::lock_guard<std::mutex> g(mMsgLock);
        mMessage = msg;
    }
    mState = State::Failed;
}

void GameDataImporter::run(fs::path root) {
    std::error_code ec;
    // Accept either the extraction root or its parent "DATA" partition folder layout.
    if (!fs::is_regular_file(root / "sys" / "main.dol", ec) && fs::is_regular_file(root / "DATA" / "sys" / "main.dol", ec)) {
        root /= "DATA";
    }
    const fs::path dol = root / "sys" / "main.dol";
    if (!fs::is_regular_file(dol, ec)) {
        fail("No sys/main.dol in that folder. Use Dolphin: right-click the game > Properties > Filesystem > "
             "right-click the disc > Extract Entire Disc, then select the output folder.");
        return;
    }
    const std::string hash = sha1_of_file(dol);
    if (hash != kExpectedDolSha1) {
        fail("main.dol does not match Super Mario Galaxy 2 (SB4E01, USA). SHA-1: " + hash);
        return;
    }
    if (!fs::is_directory(root / "files", ec)) {
        fail("Found a valid main.dol but no files/ folder next to sys/. Re-extract the entire disc.");
        return;
    }

    std::vector<fs::path> todo;
    for (const char* top : {"sys", "files"}) {
        for (auto it = fs::recursive_directory_iterator(root / top, ec); !ec && it != fs::recursive_directory_iterator(); it.increment(ec)) {
            if (it->is_regular_file(ec)) {
                todo.push_back(it->path());
            }
        }
        if (ec) {
            fail("Could not read " + (root / top).string() + ": " + ec.message());
            return;
        }
    }
    mTotal = todo.size();
    mState = State::Copying;
    for (const fs::path& src : todo) {
        const fs::path rel = fs::relative(src, root, ec);
        const fs::path dst = mGameDataDir / rel;
        fs::create_directories(dst.parent_path(), ec);
        if (!fs::copy_file(src, dst, fs::copy_options::overwrite_existing, ec)) {
            fail("Copy failed for " + rel.string() + ": " + ec.message());
            return;
        }
        mDone++;
        if ((mDone & 63) == 0) {
            std::lock_guard<std::mutex> g(mMsgLock);
            mMessage = "Copying " + rel.string();
        }
    }
    {
        std::lock_guard<std::mutex> g(mMsgLock);
        mMessage = "Imported " + std::to_string(todo.size()) + " files.";
    }
    mState = State::Done;
}

}  // namespace g2c
