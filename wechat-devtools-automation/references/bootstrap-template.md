# Bootstrap Template

Use this when a project does not yet have WeChat DevTools automation support.

## Fastest Path

Prefer the script first:

```bash
python3 scripts/bootstrap_wechat_devtools_automation.py \
  --project-dir /path/to/project \
  --env-id your-env-id \
  --functions login
```

Use `--force` only when you intentionally want to overwrite existing automation files.

After generation, run:

```bash
python3 scripts/validate_bootstrap.py \
  --project-dir /path/to/project
```

## Step 1: Add Config

Create `utils/devAutomationConfig.js` with a single exported getter:

```js
const path = require('path');

function getAutomationConfig() {
  return {
    projectPath: path.resolve(__dirname, '..'),
    devtoolsCliPath: '/Applications/wechatwebdevtools.app/Contents/MacOS/cli',
    devtoolsPort: 54448,
    envId: 'replace-with-env-id',
    defaultFunctionNames: ['login'],
    defaultCompileModeName: 'dev-tools-autorun'
  };
}

module.exports = {
  getAutomationConfig
};
```

## Step 2: Add Generated Launch Config Support

Create:

- `utils/devLaunchConfig.js`
- `utils/generatedDevLaunchConfig.js`

Requirements:

- runtime-safe static import
- `expiresAt` support
- inactive defaults committed to git

## Step 3: Add CLI Wrapper

Create `scripts/wechat-cli.sh` that reads from `getAutomationConfig()` and wraps:

- `open`
- `islogin`
- `list-functions`
- `deploy-functions`

## Step 4: Add GUI Helpers

Create:

- `scripts/wechat-gui-compile.sh`
- `scripts/wechat-gui-refresh.sh`
- `scripts/wechat-gui-capture.sh`

Requirements:

- use `osascript`
- target the project window by keyword
- avoid front-window assumptions when possible

## Step 5: Add Compile Mode Selector

Create `scripts/wechat-set-compile-mode.js`.

Requirements:

- scan DevTools localstorage files
- choose the file matching the project path
- prefer the file that actually contains the target compile mode

## Step 6: Add Diagnostics Entry

Create:

- one diagnostics page
- one diagnostics cloud function

Requirements:

- diagnostics page renders stable summaries
- diagnostics cloud function is self-contained
- diagnostics cloud function has cloud-side auth

## Step 7: Add Orchestrator

Create `scripts/wechat-regression.sh`.

Baseline behavior:

```bash
scripts/wechat-regression.sh --skip-deploy --capture-delay 10
```

It should:

1. write generated launch config with expiry
2. select compile mode
3. open project
4. verify login
5. optionally deploy functions
6. compile
7. refresh
8. capture screenshot

## Step 8: Validate

Run:

```bash
scripts/wechat-cli.sh islogin
node scripts/wechat-set-compile-mode.js
scripts/wechat-regression.sh --skip-deploy --capture-delay 10
```

Then verify:

- screenshot exists
- diagnostics page is the active route
- expected cloud function results are visible
