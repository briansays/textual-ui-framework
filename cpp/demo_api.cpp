// demo_api.cpp — in-memory reference implementation of demo_api.h.
// Replace the bodies below with calls into your real C++ system.

#include "demo_api.h"

#include <cstdlib>
#include <cstring>
#include <map>
#include <mutex>
#include <sstream>
#include <string>
#include <vector>

namespace {

struct Record {
    long id;
    std::string json;  // payload stored verbatim
};

std::mutex g_mutex;
std::map<std::string, std::vector<Record>> g_store;
std::string g_config = "{}";
long g_next_id = 1;

std::string escape(const std::string& s) {
    std::string out;
    for (char c : s) {
        switch (c) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n";  break;
            case '\t': out += "\\t";  break;
            default:   out += c;
        }
    }
    return out;
}

std::string trim(const std::string& s) {
    const auto b = s.find_first_not_of(" \t\r\n");
    if (b == std::string::npos) return "";
    const auto e = s.find_last_not_of(" \t\r\n");
    return s.substr(b, e - b + 1);
}

bool looks_like_object(const std::string& s) {
    const std::string t = trim(s);
    return t.size() >= 2 && t.front() == '{' && t.back() == '}';
}

char* to_c(const std::string& s) {
    char* out = static_cast<char*>(std::malloc(s.size() + 1));
    if (out) std::memcpy(out, s.c_str(), s.size() + 1);
    return out;
}

char* error(const std::string& msg) {
    return to_c("{\"ok\":false,\"error\":\"" + escape(msg) + "\"}");
}

}  // namespace

extern "C" {

const char* demo_api_version(void) { return "demo-api 1.0.0 (C++17)"; }

int demo_api_init(const char* config_json) {
    if (!config_json || !looks_like_object(config_json)) return 1;
    std::lock_guard<std::mutex> lock(g_mutex);
    g_config = config_json;
    return 0;
}

char* demo_api_submit(const char* entity, const char* payload_json) {
    if (!entity || !*entity) return error("entity name is required");
    if (!payload_json || !looks_like_object(payload_json))
        return error("payload must be a JSON object");
    if (std::strlen(payload_json) > 64 * 1024)
        return error("payload exceeds 64 KiB limit");

    std::lock_guard<std::mutex> lock(g_mutex);
    const long id = g_next_id++;
    g_store[entity].push_back({id, trim(payload_json)});
    return to_c("{\"ok\":true,\"id\":" + std::to_string(id) + "}");
}

char* demo_api_list(const char* entity) {
    if (!entity || !*entity) return error("entity name is required");

    std::lock_guard<std::mutex> lock(g_mutex);
    std::ostringstream out;
    out << "{\"ok\":true,\"records\":[";
    const auto it = g_store.find(entity);
    if (it != g_store.end()) {
        bool first = true;
        for (const auto& r : it->second) {
            if (!first) out << ',';
            first = false;
            out << "{\"id\":" << r.id << ",\"data\":" << r.json << '}';
        }
    }
    out << "]}";
    return to_c(out.str());
}

void demo_api_free(char* ptr) { std::free(ptr); }

void demo_api_shutdown(void) {
    std::lock_guard<std::mutex> lock(g_mutex);
    g_store.clear();
    g_next_id = 1;
}

}  // extern "C"
