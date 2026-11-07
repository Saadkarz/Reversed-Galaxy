#pragma once

// First-boot import of the user's own SMG2 (SB4E01) game files.
// Input is a folder produced by Dolphin's "Extract Entire Disc" (sys/main.dol + files/).

#include <atomic>
#include <filesystem>
#include <mutex>
#include <string>
#include <thread>

namespace g2c {

constexpr const char* kExpectedDolSha1 = "7d79810889824edd01c4ff02624713060a69818c";

class GameDataImporter {
public:
    enum class State { Idle, Verifying, Copying, Done, Failed };

    explicit GameDataImporter(std::filesystem::path gameDataDir);
    ~GameDataImporter();

    // True if gameDataDir/sys/main.dol exists and matches the SB4E01 hash.
    bool hasValidGameData() const;

    // Starts verification + copy on a worker thread.
    void start(const std::filesystem::path& extractedRoot);

    State state() const { return mState.load(); }
    float progress() const;
    std::string message() const;
    const std::filesystem::path& gameDataDir() const { return mGameDataDir; }

private:
    void run(std::filesystem::path root);
    void fail(const std::string& msg);

    std::filesystem::path mGameDataDir;
    std::atomic<State> mState{State::Idle};
    std::atomic<unsigned long long> mDone{0};
    std::atomic<unsigned long long> mTotal{0};
    mutable std::mutex mMsgLock;
    std::string mMessage;
    std::thread mWorker;
};

// Returns the SHA-1 (lower-case hex) of a file, or an empty string on read failure.
std::string sha1_of_file(const std::filesystem::path& path);

}  // namespace g2c
