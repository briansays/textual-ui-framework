/*
 * demo_api.h — a deliberately generic C-ABI facade over a C++ backend.
 *
 * Every call exchanges JSON text so the UI layer never needs to know about
 * C++ types. Swap the implementation in demo_api.cpp for your real system;
 * keep this header stable and the Textual front end keeps working.
 *
 * Memory: any `char*` returned by a demo_api_* function is heap-allocated
 * by the library and MUST be released with demo_api_free().
 */
#ifndef DEMO_API_H
#define DEMO_API_H

#ifdef __cplusplus
extern "C" {
#endif

/* Static version string, e.g. "demo-api 1.0.0 (C++17)". Do not free. */
const char* demo_api_version(void);

/* Initialise / reconfigure the backend. config_json is a JSON object.
 * Returns 0 on success, non-zero on failure. */
int demo_api_init(const char* config_json);

/* Store a record under `entity` (e.g. "customers").
 * Returns {"ok":true,"id":N} or {"ok":false,"error":"..."}. */
char* demo_api_submit(const char* entity, const char* payload_json);

/* List every record for `entity`.
 * Returns {"ok":true,"records":[{"id":N,"data":{...}}, ...]}. */
char* demo_api_list(const char* entity);

/* Release a string returned by this library. */
void demo_api_free(char* ptr);

/* Tear down backend state. */
void demo_api_shutdown(void);

#ifdef __cplusplus
}
#endif

#endif /* DEMO_API_H */
