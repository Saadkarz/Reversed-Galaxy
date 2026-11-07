// Galaxy2Coop: boot runtime + first-boot launcher (Step 1).

#include "dispatch.hpp"
#include "dol.hpp"
#include "launcher.hpp"
#include "memory.hpp"
#include "smoke_test.hpp"

#include <SDL3/SDL.h>
#include <imgui.h>
#include <imgui_impl_sdl3.h>
#include <imgui_impl_sdlrenderer3.h>

#include <cstdio>
#include <filesystem>
#include <memory>
#include <mutex>
#include <optional>
#include <string>
#include <vector>

namespace fs = std::filesystem;

namespace {

struct FolderPick {
    std::mutex lock;
    std::optional<std::string> path;
    bool pending = false;
};

void SDLCALL onFolderChosen(void* userdata, const char* const* filelist, int) {
    auto* pick = static_cast<FolderPick*>(userdata);
    std::lock_guard<std::mutex> g(pick->lock);
    pick->pending = false;
    if (filelist != nullptr && filelist[0] != nullptr) {
        pick->path = filelist[0];
    }
}

fs::path exeDir() {
    const char* base = SDL_GetBasePath();
    return base ? fs::path(base) : fs::current_path();
}

struct BootState {
    bool loaded = false;
    std::string error;
    g2c::DolImage dol;
    std::unique_ptr<g2c::WiiMemory> mem;
    std::vector<g2c::SmokeResult> smoke;
};

void bootGame(BootState& st, const fs::path& gameData) {
    st = BootState{};
    std::vector<g2c::u8> bytes;
    const fs::path dolPath = gameData / "sys" / "main.dol";
    if (!g2c::read_file(dolPath.string(), bytes)) {
        st.error = "Could not read " + dolPath.string();
        return;
    }
    if (!g2c::parse_dol(bytes, st.dol, st.error)) {
        return;
    }
    st.mem = std::make_unique<g2c::WiiMemory>();
    g2c::load_dol(st.dol, *st.mem);
    g2c_register_all();
    st.loaded = true;
}

}  // namespace

// Headless check: Galaxy2Coop --smoke <path to main.dol>  (exit code 0 = all pass)
int runHeadlessSmoke(const char* dolPath) {
    std::vector<g2c::u8> bytes;
    g2c::DolImage dol;
    std::string err;
    if (!g2c::read_file(dolPath, bytes) || !g2c::parse_dol(bytes, dol, err)) {
        std::fprintf(stderr, "cannot load %s %s\n", dolPath, err.c_str());
        return 2;
    }
    const std::string hash = g2c::sha1_of_file(dolPath);
    std::printf("main.dol SHA-1 %s (%s)\n", hash.c_str(), hash == g2c::kExpectedDolSha1 ? "SB4E01 OK" : "MISMATCH");
    auto mem = std::make_unique<g2c::WiiMemory>();
    g2c::load_dol(dol, *mem);
    g2c_register_all();
    std::printf("registered %zu lifted functions; %s\n", g2c::registered_func_count(), g2c_lift_stats);
    int fails = 0;
    for (const auto& r : g2c::run_smoke_tests(*mem)) {
        std::printf("%s  %s  (%s)\n", r.pass ? "PASS" : "FAIL", r.name.c_str(), r.detail.c_str());
        fails += r.pass ? 0 : 1;
    }
    return fails ? 1 : 0;
}

int main(int argc, char** argv) {
    if (argc == 3 && std::string(argv[1]) == "--smoke") {
        return runHeadlessSmoke(argv[2]);
    }
    if (argc == 3 && std::string(argv[1]) == "--import") {
        // Headless first-boot import (same path as the launcher's folder picker).
        g2c::GameDataImporter importer(exeDir() / "game_data");
        importer.start(argv[2]);
        while (importer.state() == g2c::GameDataImporter::State::Verifying ||
               importer.state() == g2c::GameDataImporter::State::Copying) {
            SDL_Delay(20);
        }
        std::printf("%s\n", importer.message().c_str());
        return importer.state() == g2c::GameDataImporter::State::Done && importer.hasValidGameData() ? 0 : 1;
    }
    if (!SDL_Init(SDL_INIT_VIDEO)) {
        std::fprintf(stderr, "SDL_Init failed: %s\n", SDL_GetError());
        return 1;
    }
    SDL_Window* window = SDL_CreateWindow("Galaxy2Coop", 1280, 720, SDL_WINDOW_RESIZABLE | SDL_WINDOW_HIGH_PIXEL_DENSITY);
    SDL_Renderer* renderer = window ? SDL_CreateRenderer(window, nullptr) : nullptr;
    if (renderer == nullptr) {
        std::fprintf(stderr, "window/renderer creation failed: %s\n", SDL_GetError());
        return 1;
    }
    SDL_SetRenderVSync(renderer, 1);

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGui::GetIO().IniFilename = nullptr;
    ImGui::StyleColorsDark();
    ImGui_ImplSDL3_InitForSDLRenderer(window, renderer);
    ImGui_ImplSDLRenderer3_Init(renderer);

    g2c::GameDataImporter importer(exeDir() / "game_data");
    FolderPick pick;
    BootState boot;
    bool haveData = importer.hasValidGameData();
    if (haveData) {
        bootGame(boot, importer.gameDataDir());
    }

    bool running = true;
    while (running) {
        SDL_Event e;
        while (SDL_PollEvent(&e)) {
            ImGui_ImplSDL3_ProcessEvent(&e);
            if (e.type == SDL_EVENT_QUIT) {
                running = false;
            }
        }

        {
            std::lock_guard<std::mutex> g(pick.lock);
            if (pick.path) {
                importer.start(*pick.path);
                pick.path.reset();
            }
        }
        if (!haveData && importer.state() == g2c::GameDataImporter::State::Done) {
            haveData = true;
            bootGame(boot, importer.gameDataDir());
        }

        ImGui_ImplSDLRenderer3_NewFrame();
        ImGui_ImplSDL3_NewFrame();
        ImGui::NewFrame();

        const ImGuiViewport* vp = ImGui::GetMainViewport();
        ImGui::SetNextWindowPos(vp->WorkPos);
        ImGui::SetNextWindowSize(vp->WorkSize);
        ImGui::Begin("Galaxy2Coop", nullptr, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove);
        ImGui::Text("Galaxy2Coop - Super Mario Galaxy 2 native port (Step 1: boot runtime)");
        ImGui::Separator();

        if (!haveData) {
            ImGui::TextWrapped("First boot: select the folder you extracted from your own SMG2 (SB4E01) disc with Dolphin "
                               "(right-click the game > Properties > Filesystem > right-click the disc > Extract Entire Disc).");
            const auto st = importer.state();
            const bool busy = st == g2c::GameDataImporter::State::Verifying || st == g2c::GameDataImporter::State::Copying;
            ImGui::BeginDisabled(busy || pick.pending);
            if (ImGui::Button("Select extracted SMG2 folder...")) {
                pick.pending = true;
                SDL_ShowOpenFolderDialog(onFolderChosen, &pick, window, nullptr, false);
            }
            ImGui::EndDisabled();
            if (st != g2c::GameDataImporter::State::Idle) {
                ImGui::TextWrapped("%s", importer.message().c_str());
            }
            if (st == g2c::GameDataImporter::State::Copying) {
                ImGui::ProgressBar(importer.progress());
            }
        } else if (!boot.loaded) {
            ImGui::TextColored(ImVec4(1, 0.4f, 0.4f, 1), "Boot failed: %s", boot.error.c_str());
        } else {
            ImGui::Text("Game data: %s", importer.gameDataDir().string().c_str());
            ImGui::Text("main.dol verified (SHA-1 %s), entry point 0x%08X", g2c::kExpectedDolSha1, boot.dol.entryPoint);
            if (ImGui::BeginTable("sections", 4, ImGuiTableFlags_Borders | ImGuiTableFlags_RowBg)) {
                ImGui::TableSetupColumn("Section");
                ImGui::TableSetupColumn("Address");
                ImGui::TableSetupColumn("Size");
                ImGui::TableSetupColumn("File offset");
                ImGui::TableHeadersRow();
                int ti = 0, di = 0;
                for (const auto& s : boot.dol.sections) {
                    ImGui::TableNextRow();
                    ImGui::TableNextColumn();
                    ImGui::Text("%s%d", s.isText ? "text" : "data", s.isText ? ti++ : di++);
                    ImGui::TableNextColumn();
                    ImGui::Text("0x%08X", s.address);
                    ImGui::TableNextColumn();
                    ImGui::Text("0x%X", s.size);
                    ImGui::TableNextColumn();
                    ImGui::Text("0x%X", s.fileOffset);
                }
                ImGui::EndTable();
            }
            ImGui::Text("BSS 0x%08X (+0x%X)  |  MEM1 24 MiB, MEM2 64 MiB mapped", boot.dol.bssAddress, boot.dol.bssSize);
            ImGui::Text("Lifted functions registered: %zu", g2c::registered_func_count());
            ImGui::TextWrapped("Lifter: %s", g2c_lift_stats);
            if (ImGui::Button("Run smoke test")) {
                boot.smoke = g2c::run_smoke_tests(*boot.mem);
            }
            for (const auto& r : boot.smoke) {
                ImGui::TextColored(r.pass ? ImVec4(0.4f, 1, 0.4f, 1) : ImVec4(1, 0.4f, 0.4f, 1), "%s  %s  (%s)",
                                   r.pass ? "PASS" : "FAIL", r.name.c_str(), r.detail.c_str());
            }
        }
        ImGui::End();

        ImGui::Render();
        SDL_SetRenderDrawColorFloat(renderer, 0.06f, 0.06f, 0.10f, 1.0f);
        SDL_RenderClear(renderer);
        ImGui_ImplSDLRenderer3_RenderDrawData(ImGui::GetDrawData(), renderer);
        SDL_RenderPresent(renderer);
    }

    ImGui_ImplSDLRenderer3_Shutdown();
    ImGui_ImplSDL3_Shutdown();
    ImGui::DestroyContext();
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
