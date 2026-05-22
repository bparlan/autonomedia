# Findings: Ad-hoc Scripting Limitations

## Core Limitations Identified (from M2/M3)
- **Session Fragility**: Ad-hoc scripts lose session context easily if they crash or exit abruptly.
- **Race Conditions**: Without an orchestrated loop, DOM elements are often accessed before the page is "actually" ready (e.g., login vs dashboard).
- **Rate Limiting**: Sequential, immediate execution triggers server-side protections (e.g., "Something went wrong").
- **Error Recovery**: Scripts exit on error; a worker system must catch, log, and potentially retry without killing the environment.

## Key Design Principles for M5
- **Persistence**: The worker should keep the browser instance alive across multiple tasks.
- **Backoff**: Implement exponential backoff for platform errors.
- **Isolation**: Each platform adapter should be a distinct task handler.
