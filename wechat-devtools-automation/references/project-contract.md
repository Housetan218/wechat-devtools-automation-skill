# Project Contract

Use this file when adapting a new WeChat Mini Program project to the shared automation workflow.

## Minimum Files

Create these project-local files or their equivalent:

- `utils/devAutomationConfig.js`
- `utils/devLaunchConfig.js`
- `utils/generatedDevLaunchConfig.js`
- `scripts/wechat-cli.sh`
- `scripts/wechat-set-compile-mode.js`
- `scripts/wechat-gui-compile.sh`
- `scripts/wechat-gui-refresh.sh`
- `scripts/wechat-gui-capture.sh`
- `scripts/wechat-regression.sh`

## Minimum Config Fields

`utils/devAutomationConfig.js` should expose one function returning:

- `projectPath`
- `devtoolsPort`
- `envId` or `cloudEnvId`
- `defaultFunctionNames`
- `defaultCompileModeName`

Optional:

- `devtoolsCliPath`
- `projectWindowKeyword`
- `diagnosticsPagePath`
- `defaultCaptureDelaySeconds`

## Mini Program Runtime Support

The project should include:

- one diagnostics page, for example `pages/dev-tools/dev-tools`
- one generated launch config module, statically required by runtime code
- one guarded runtime redirect path in `app.js` or a page entry only as fallback

The generated launch config should contain:

- `enabled`
- `path`
- `onceToken`
- `waitMs`
- `expiresAt`

The runtime guard should refuse expired configs.

## Compile Mode Contract

`project.config.json` should contain one compile mode entry with:

- stable `name`
- diagnostics page `pathName`
- fixed `query`

The compile mode selector script should:

- scan all DevTools localstorage files for the current project
- choose the one containing the desired mode
- set `condiction.weapp.current`

## Diagnostics Contract

The diagnostics route should be good for automation:

- render stable summary cards
- avoid random animation or lazy content that changes screenshot timing
- expose structured error text on failure
- call cloud functions that are self-contained and independently deployable

The diagnostics cloud function should:

- enforce admin auth before returning global data
- use deterministic queries and explicit sort order
- avoid cross-function relative imports

## Regression Script Behavior

The orchestrator should:

1. select compile mode
2. open project
3. verify login
4. optionally deploy selected functions
5. trigger compile
6. trigger refresh
7. wait a bounded amount of time
8. capture screenshot
9. write artifacts and next-step notes

## Output Contract

Save artifacts under:

- `tmp/wechat-regression/<run-id>/cli.log`
- `tmp/wechat-regression/<run-id>/dev-tools.png`
- `tmp/wechat-regression/<run-id>/next-step.txt`

This keeps future review and comparison simple.
