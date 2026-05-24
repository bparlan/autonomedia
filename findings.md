# Findings: Ad-hoc Scripting Limitations

## Core Limitations Identified (from M2/M3)
- **Session Fragility**: Ad-hoc scripts lose session context easily if they crash or exit abruptly.
- **Race Conditions**: Without an orchestrated loop, DOM elements are often accessed before the page is "actually" ready (e.g., login vs dashboard).
- **Rate Limiting**: Sequential, immediate execution triggers server-side protections (e.g., "Something went wrong").
- **Error Recovery**: Scripts exit on error; a worker system must catch, log, and potentially retry without killing the environment.

## M52 Findings
- **Platform Coupling**: Hardcoded if-else in worker creates bottleneck.
- **Browser Lifecycle**: Boilerplate across platforms requires abstraction.
- **Error Visibility**: Need unified artifact capture (logs/screenshots) on failure.
