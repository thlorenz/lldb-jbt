# lldb-jbt

![assets/sample.png](assets/sample.png)

## Installation

```
npm install -g lldb-jbt
```

## Usage

1. Add the script dir to your `PYTHONPATH` by running `source jbt`
2. Debug your node process with `--perf-basic-prof` flag, i.e. `lldb -- node --perf-basic-prof index.js`
3. Import the **jbt** command into lldb `command script import jbt`
4. Set a breakpoint, i.e. `b uv_fs_read`
5. When you hit the breakpoint type `jbt` to see the stack trace with JavaScript symbols resolved

## Status

**MAD SCIENCE!!**

## License

MIT
