# Third-party runtime

The generated preview includes stlite 1.8.1, Streamlit 1.57.0, Pyodide 0.29.3, and their runtime dependencies.

- stlite: [source and license](https://github.com/whitphx/stlite/tree/@stlite/browser@1.8.1), Apache License 2.0. The version-specific license is included as `STLITE-LICENSE.txt`.
- Streamlit: [source](https://github.com/streamlit/streamlit/tree/1.57.0), Apache License 2.0. Its bundled wheel retains distribution metadata and licensing files.
- Pyodide: [source and licenses](https://github.com/pyodide/pyodide/tree/0.29.3), Mozilla Public License 2.0 and component licenses. Its packages retain their wheel metadata and included licenses.

The runtime lock lists exact upstream asset URLs and SHA-256 hashes. Preserve the vendor wheels and these notices when distributing a preview.

Balanced Books applies one browser compatibility change to the pinned stlite frontend after verifying its original archive: skip the legacy component HTTP reachability probe for the synthetic `stlite.invalid` kernel origin. Both local component frames remain served through stlite's kernel. `manifest.json` records the modified file and SHA-256 hash; the original stlite license remains included. No server deployment file is changed.
