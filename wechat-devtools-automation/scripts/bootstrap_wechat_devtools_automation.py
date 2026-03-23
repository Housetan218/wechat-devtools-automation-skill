#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import stat
from pathlib import Path


CLI_WRAPPER = """#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

read_config() {
  local key="$1"
  node -e "const { getAutomationConfig } = require('${ROOT_DIR}/utils/devAutomationConfig'); const c = getAutomationConfig(); const value = c['${key}']; if (Array.isArray(value)) { console.log(value.join(',')); } else { console.log(value); }"
}

CLI_PATH="$(read_config devtoolsCliPath)"
PROJECT_PATH="$(read_config projectPath)"
PORT="$(read_config devtoolsPort)"
ENV_ID="$(read_config envId)"

if [[ ! -x "${CLI_PATH}" ]]; then
  echo "[wechat-cli] CLI not found or not executable: ${CLI_PATH}" >&2
  exit 1
fi

run_cli() {
  "${CLI_PATH}" "$@" --project "${PROJECT_PATH}" --port "${PORT}"
}

COMMAND="${1:-}"
shift || true

case "${COMMAND}" in
  islogin)
    run_cli islogin "$@"
    ;;
  open)
    run_cli open "$@"
    ;;
  close)
    run_cli close "$@"
    ;;
  quit)
    run_cli quit "$@"
    ;;
  list-functions)
    run_cli cloud functions list -e "${ENV_ID}" "$@"
    ;;
  deploy-functions)
    if [[ $# -eq 0 ]]; then
      echo "[wechat-cli] deploy-functions requires at least one function name" >&2
      exit 1
    fi
    run_cli cloud functions deploy -e "${ENV_ID}" -n "$@" --provided --remote-npm-install
    ;;
  *)
    cat <<'EOF' >&2
Usage:
  scripts/wechat-cli.sh islogin
  scripts/wechat-cli.sh open
  scripts/wechat-cli.sh close
  scripts/wechat-cli.sh quit
  scripts/wechat-cli.sh list-functions
  scripts/wechat-cli.sh deploy-functions <name...>
EOF
    exit 1
    ;;
esac
"""


GUI_COMPILE = """#!/usr/bin/env bash
set -euo pipefail

PROCESS_NAME="${WECHAT_DEVTOOLS_PROCESS_NAME:-微信开发者工具}"
WINDOW_KEYWORD="${WECHAT_DEVTOOLS_WINDOW_KEYWORD:-}"
ACTIVATE_DELAY_MS="${WECHAT_COMPILE_ACTIVATE_DELAY_MS:-1200}"

activate_delay_seconds="$(node -e "console.log((Number(process.argv[1]) || 1200) / 1000)" "${ACTIVATE_DELAY_MS}")"

osascript <<OSA
tell application "System Events"
  if not (exists process "${PROCESS_NAME}") then
    error "process not found: ${PROCESS_NAME}"
  end if

  tell process "${PROCESS_NAME}"
    set frontmost to true
    delay ${activate_delay_seconds}

    if "${WINDOW_KEYWORD}" is not "" then
      repeat with candidateWindow in every window
        try
          if (name of candidateWindow) contains "${WINDOW_KEYWORD}" then
            perform action "AXRaise" of candidateWindow
            exit repeat
          end if
        end try
      end repeat
    end if

    keystroke "b" using command down
  end tell
end tell
OSA

echo "[wechat-gui-compile] triggered compile"
"""


GUI_REFRESH = """#!/usr/bin/env bash
set -euo pipefail

PROCESS_NAME="${WECHAT_DEVTOOLS_PROCESS_NAME:-微信开发者工具}"
WINDOW_KEYWORD="${WECHAT_DEVTOOLS_WINDOW_KEYWORD:-}"
ACTIVATE_DELAY_MS="${WECHAT_REFRESH_ACTIVATE_DELAY_MS:-1200}"

activate_delay_seconds="$(node -e "console.log((Number(process.argv[1]) || 1200) / 1000)" "${ACTIVATE_DELAY_MS}")"

osascript <<OSA
tell application "System Events"
  if not (exists process "${PROCESS_NAME}") then
    error "process not found: ${PROCESS_NAME}"
  end if

  tell process "${PROCESS_NAME}"
    set frontmost to true
    delay ${activate_delay_seconds}

    if "${WINDOW_KEYWORD}" is not "" then
      repeat with candidateWindow in every window
        try
          if (name of candidateWindow) contains "${WINDOW_KEYWORD}" then
            perform action "AXRaise" of candidateWindow
            exit repeat
          end if
        end try
      end repeat
    end if

    keystroke "r" using command down
  end tell
end tell
OSA

echo "[wechat-gui-refresh] triggered refresh"
"""


GUI_CAPTURE = """#!/usr/bin/env bash
set -euo pipefail

OUTPUT_PATH="${1:-}"
PROCESS_NAME="${WECHAT_DEVTOOLS_PROCESS_NAME:-微信开发者工具}"
WINDOW_KEYWORD="${WECHAT_DEVTOOLS_WINDOW_KEYWORD:-}"
ACTIVATE_DELAY_MS="${WECHAT_CAPTURE_ACTIVATE_DELAY_MS:-1500}"

if [[ -z "${OUTPUT_PATH}" ]]; then
  echo "Usage: scripts/wechat-gui-capture.sh <output-path>" >&2
  exit 1
fi

mkdir -p "$(dirname "${OUTPUT_PATH}")"

activate_delay_seconds="$(node -e "console.log((Number(process.argv[1]) || 1500) / 1000)" "${ACTIVATE_DELAY_MS}")"

bounds="$(
  osascript <<OSA
tell application "System Events"
  if not (exists process "${PROCESS_NAME}") then
    error "process not found: ${PROCESS_NAME}"
  end if

  tell process "${PROCESS_NAME}"
    set frontmost to true
    delay ${activate_delay_seconds}
    set targetWindow to front window

    if "${WINDOW_KEYWORD}" is not "" then
      repeat with candidateWindow in every window
        try
          if (name of candidateWindow) contains "${WINDOW_KEYWORD}" then
            set targetWindow to candidateWindow
            exit repeat
          end if
        end try
      end repeat
    end if

    try
      perform action "AXRaise" of targetWindow
      delay 0.3
    end try

    set {xPos, yPos} to position of targetWindow
    set {winWidth, winHeight} to size of targetWindow
    return (xPos as text) & "," & (yPos as text) & "," & (winWidth as text) & "," & (winHeight as text)
  end tell
end tell
OSA
)"

if [[ -z "${bounds}" ]]; then
  echo "[wechat-gui-capture] failed to resolve window bounds" >&2
  exit 1
fi

screencapture -x -R "${bounds}" "${OUTPUT_PATH}"
echo "[wechat-gui-capture] captured ${OUTPUT_PATH} bounds=${bounds}"
"""


COMPILE_MODE_JS = """#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { getAutomationConfig } = require('../utils/devAutomationConfig');

function findProjectLocalStorageFiles(rootDir, projectPath) {
  const matches = [];
  const entries = fs.readdirSync(rootDir, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isDirectory()) {
      continue;
    }

    const localDataDir = path.join(rootDir, entry.name, 'WeappLocalData');
    if (!fs.existsSync(localDataDir)) {
      continue;
    }

    const names = fs.readdirSync(localDataDir).filter((name) => name.startsWith('localstorage_') && name.endsWith('.json'));
    for (const name of names) {
      const filePath = path.join(localDataDir, name);
      try {
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        if (data.projectid === projectPath || data.projectpath === projectPath) {
          matches.push(filePath);
        }
      } catch (error) {
        continue;
      }
    }
  }

  return matches;
}

function findProjectLocalStorageFile(rootDir, projectPath, modeName) {
  const matches = findProjectLocalStorageFiles(rootDir, projectPath);
  if (matches.length === 0) {
    return '';
  }

  if (!modeName) {
    return matches[0];
  }

  const preferred = matches.find((filePath) => {
    try {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      const condition = data.condiction || data.condition || {};
      const weapp = condition.weapp || condition.miniprogram || {};
      const list = Array.isArray(weapp.list) ? weapp.list : [];
      return list.some((item) => item && item.name === modeName);
    } catch (error) {
      return false;
    }
  });

  return preferred || matches[0];
}

function setCompileMode({ filePath, modeName }) {
  const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const condition = data.condiction || data.condition || {};
  const weapp = condition.weapp || condition.miniprogram || { current: -1, list: [] };
  const list = Array.isArray(weapp.list) ? weapp.list : [];
  const index = list.findIndex((item) => item && item.name === modeName);

  if (index < 0) {
    throw new Error(`compile mode not found: ${modeName}`);
  }

  weapp.current = index;
  condition.weapp = weapp;
  data.condiction = condition;
  fs.writeFileSync(filePath, JSON.stringify(data));

  return {
    filePath,
    modeName,
    current: index
  };
}

function main() {
  const { projectPath, defaultCompileModeName } = getAutomationConfig();
  const modeName = process.argv[2] || defaultCompileModeName;
  const rootDir = path.join(process.env.HOME, 'Library/Application Support/微信开发者工具');
  const filePath = findProjectLocalStorageFile(rootDir, projectPath, modeName);

  if (!filePath) {
    throw new Error(`localstorage file not found for project: ${projectPath}`);
  }

  const result = setCompileMode({ filePath, modeName });
  console.log(JSON.stringify(result, null, 2));
}

if (require.main === module) {
  try {
    main();
  } catch (error) {
    console.error(`[wechat-set-compile-mode] ${error.message}`);
    process.exit(1);
  }
}

module.exports = {
  findProjectLocalStorageFiles,
  findProjectLocalStorageFile,
  setCompileMode
};
"""


REGRESSION_SH = """#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI_SCRIPT="${ROOT_DIR}/scripts/wechat-cli.sh"
SET_COMPILE_MODE_SCRIPT="${ROOT_DIR}/scripts/wechat-set-compile-mode.js"
CAPTURE_SCRIPT="${ROOT_DIR}/scripts/wechat-gui-capture.sh"
COMPILE_SCRIPT="${ROOT_DIR}/scripts/wechat-gui-compile.sh"
REFRESH_SCRIPT="${ROOT_DIR}/scripts/wechat-gui-refresh.sh"
OUTPUT_DIR="${ROOT_DIR}/tmp/wechat-regression/$(date '+%Y%m%d-%H%M%S')"
PROJECT_WINDOW_KEYWORD="$(node -e "const path=require('path'); const { getAutomationConfig } = require('${ROOT_DIR}/utils/devAutomationConfig'); console.log(path.basename(getAutomationConfig().projectPath));")"
FUNCTIONS=""
SKIP_DEPLOY="false"
SKIP_CAPTURE="false"
CAPTURE_DELAY_SECONDS="${WECHAT_CAPTURE_DELAY_SECONDS:-18}"
DEV_LAUNCH_CONFIG_PATH="${ROOT_DIR}/utils/generatedDevLaunchConfig.js"
DIAGNOSTICS_ROUTE="__DIAGNOSTICS_ROUTE__"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --functions)
      FUNCTIONS="${2:-}"
      shift 2
      ;;
    --skip-deploy)
      SKIP_DEPLOY="true"
      shift
      ;;
    --skip-capture)
      SKIP_CAPTURE="true"
      shift
      ;;
    --capture-delay)
      CAPTURE_DELAY_SECONDS="${2:-}"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="${2:-}"
      shift 2
      ;;
    *)
      echo "[wechat-regression] unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

mkdir -p "${OUTPUT_DIR}"

write_dev_launch_config() {
  local once_token="$1"
  local expires_at_ms
  expires_at_ms="$(node -e "console.log(Date.now() + 5 * 60 * 1000)")"
  cat >"${DEV_LAUNCH_CONFIG_PATH}" <<EOF
module.exports = {
  enabled: true,
  path: '${DIAGNOSTICS_ROUTE}',
  onceToken: '${once_token}',
  waitMs: 1800,
  expiresAt: ${expires_at_ms}
};
EOF
}

cleanup_dev_launch_config() {
  cat >"${DEV_LAUNCH_CONFIG_PATH}" <<'EOF'
module.exports = {
  enabled: false,
  path: '',
  onceToken: '',
  waitMs: 1200,
  expiresAt: 0
};
EOF
}

trap cleanup_dev_launch_config EXIT

RUN_TOKEN="wechat-regression-$(date '+%Y%m%d-%H%M%S')"
write_dev_launch_config "${RUN_TOKEN}"

{
  echo "[wechat-regression] output_dir=${OUTPUT_DIR}"
  echo "[wechat-regression] select compile mode"
  node "${SET_COMPILE_MODE_SCRIPT}"

  echo "[wechat-regression] open project"
  "${CLI_SCRIPT}" open

  echo "[wechat-regression] check login"
  "${CLI_SCRIPT}" islogin

  echo "[wechat-regression] list cloud functions"
  "${CLI_SCRIPT}" list-functions

  if [[ "${SKIP_DEPLOY}" != "true" ]]; then
    if [[ -z "${FUNCTIONS}" ]]; then
      FUNCTIONS="$(node -e "const { getAutomationConfig } = require('${ROOT_DIR}/utils/devAutomationConfig'); console.log(getAutomationConfig().defaultFunctionNames.join(' '));")"
    else
      FUNCTIONS="$(echo "${FUNCTIONS}" | tr ',' ' ')"
    fi

    echo "[wechat-regression] deploy functions: ${FUNCTIONS}"
    # shellcheck disable=SC2086
    "${CLI_SCRIPT}" deploy-functions ${FUNCTIONS}
  fi
} | tee "${OUTPUT_DIR}/cli.log"

echo "[wechat-regression] trigger local compile" | tee -a "${OUTPUT_DIR}/cli.log"
WECHAT_DEVTOOLS_WINDOW_KEYWORD="${PROJECT_WINDOW_KEYWORD}" "${COMPILE_SCRIPT}" | tee -a "${OUTPUT_DIR}/cli.log"
sleep 2
echo "[wechat-regression] trigger local refresh" | tee -a "${OUTPUT_DIR}/cli.log"
WECHAT_DEVTOOLS_WINDOW_KEYWORD="${PROJECT_WINDOW_KEYWORD}" "${REFRESH_SCRIPT}" | tee -a "${OUTPUT_DIR}/cli.log"

if [[ "${SKIP_CAPTURE}" != "true" ]]; then
  echo "[wechat-regression] wait ${CAPTURE_DELAY_SECONDS}s for diagnostics autorun" | tee -a "${OUTPUT_DIR}/cli.log"
  sleep "${CAPTURE_DELAY_SECONDS}"
  WECHAT_DEVTOOLS_WINDOW_KEYWORD="${PROJECT_WINDOW_KEYWORD}" "${CAPTURE_SCRIPT}" "${OUTPUT_DIR}/dev-tools.png" | tee -a "${OUTPUT_DIR}/cli.log"
fi

cat <<EOF | tee "${OUTPUT_DIR}/next-step.txt"
CLI automation completed.

Artifacts:
1. CLI log: ${OUTPUT_DIR}/cli.log
2. Screenshot: ${OUTPUT_DIR}/dev-tools.png

Current automation route:
${DIAGNOSTICS_ROUTE}

TODO:
- Add a diagnostics page at the route above
- Add a guarded diagnostics cloud function before exposing global data
EOF
"""


DEV_AUTOMATION_CONFIG = """const path = require('path');

const DEFAULT_DEVTOOLS_CLI_PATH = '/Applications/wechatwebdevtools.app/Contents/MacOS/cli';
const DEFAULT_DEVTOOLS_PORT = {devtools_port};
const DEFAULT_ENV_ID = '{env_id}';
const DEFAULT_FUNCTION_NAMES = {functions};
const DEFAULT_COMPILE_MODE_NAME = '{compile_mode_name}';

function getProjectPath() {{
  return path.resolve(__dirname, '..');
}}

function parsePort(value) {{
  const port = Number(value);
  return Number.isFinite(port) && port > 0 ? port : DEFAULT_DEVTOOLS_PORT;
}}

function splitFunctionNames(value) {{
  if (!value) {{
    return [...DEFAULT_FUNCTION_NAMES];
  }}

  return String(value)
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}}

function getAutomationConfig() {{
  return {{
    projectPath: getProjectPath(),
    devtoolsCliPath: process.env.WECHAT_DEVTOOLS_CLI_PATH || DEFAULT_DEVTOOLS_CLI_PATH,
    devtoolsPort: parsePort(process.env.WECHAT_DEVTOOLS_PORT),
    envId: process.env.WECHAT_CLOUD_ENV_ID || DEFAULT_ENV_ID,
    defaultFunctionNames: splitFunctionNames(process.env.WECHAT_DEFAULT_FUNCTIONS),
    defaultCompileModeName: process.env.WECHAT_DEFAULT_COMPILE_MODE || DEFAULT_COMPILE_MODE_NAME
  }};
}}

module.exports = {{
  DEFAULT_DEVTOOLS_CLI_PATH,
  DEFAULT_DEVTOOLS_PORT,
  DEFAULT_ENV_ID,
  DEFAULT_FUNCTION_NAMES,
  DEFAULT_COMPILE_MODE_NAME,
  getProjectPath,
  getAutomationConfig,
  splitFunctionNames
}};
"""


DEV_LAUNCH_CONFIG = """const DEFAULT_DEV_LAUNCH_CONFIG = Object.freeze({
  enabled: false,
  path: '',
  onceToken: '',
  waitMs: 1200,
  expiresAt: 0
});

function normalizePositiveNumber(value, fallback) {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : fallback;
}

function sanitizeLaunchConfig(input) {
  const config = input && typeof input === 'object' ? input : {};
  const path = typeof config.path === 'string' ? config.path.trim() : '';

  return {
    enabled: Boolean(config.enabled && path),
    path,
    onceToken: typeof config.onceToken === 'string' ? config.onceToken.trim() : '',
    waitMs: normalizePositiveNumber(config.waitMs, DEFAULT_DEV_LAUNCH_CONFIG.waitMs),
    expiresAt: normalizePositiveNumber(config.expiresAt, DEFAULT_DEV_LAUNCH_CONFIG.expiresAt)
  };
}

function loadGeneratedOverride(loadModule) {
  const moduleLoader = loadModule || (() => require('./generatedDevLaunchConfig.js'));
  try {
    return sanitizeLaunchConfig(moduleLoader());
  } catch (error) {
    if (error && error.code === 'MODULE_NOT_FOUND') {
      return { ...DEFAULT_DEV_LAUNCH_CONFIG };
    }
    throw error;
  }
}

function getDevLaunchConfig(loadModule) {
  return loadGeneratedOverride(loadModule);
}

function isLaunchConfigActive(config, nowMs = Date.now()) {
  if (!config || !config.enabled || !config.path) {
    return false;
  }

  if (!config.expiresAt) {
    return true;
  }

  return nowMs <= config.expiresAt;
}

module.exports = {
  DEFAULT_DEV_LAUNCH_CONFIG,
  getDevLaunchConfig,
  isLaunchConfigActive,
  loadGeneratedOverride,
  sanitizeLaunchConfig
};
"""


GENERATED_DEV_LAUNCH_CONFIG = """module.exports = {
  enabled: false,
  path: '',
  onceToken: '',
  waitMs: 1200,
  expiresAt: 0
};
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap WeChat DevTools automation files into a project")
    parser.add_argument("--project-dir", required=True, help="Target WeChat Mini Program project directory")
    parser.add_argument("--env-id", default="replace-with-env-id", help="Tencent cloud env id")
    parser.add_argument("--functions", default="login", help="Comma-separated default function names")
    parser.add_argument("--compile-mode-name", default="dev-tools-autorun", help="Compile mode name")
    parser.add_argument("--diagnostics-page", default="pages/dev-tools/dev-tools", help="Diagnostics page path without leading slash")
    parser.add_argument("--diagnostics-query", default="autorun=1&capture=1&testType=all", help="Default diagnostics query")
    parser.add_argument("--devtools-port", type=int, default=54448, help="WeChat DevTools HTTP service port")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    return parser.parse_args()


def write_file(path: Path, content: str, executable: bool, force: bool) -> str:
    if path.exists() and not force:
        return "skipped"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return "written"


def ensure_compile_mode(project_config_path: Path, compile_mode_name: str, diagnostics_page: str, diagnostics_query: str) -> str:
    if not project_config_path.exists():
        return "missing-project-config"

    data = json.loads(project_config_path.read_text(encoding="utf-8"))
    condition = data.get("condition")
    if not isinstance(condition, dict):
        condition = {}
        data["condition"] = condition

    mini = condition.get("miniprogram")
    if not isinstance(mini, dict):
        mini = {}
        condition["miniprogram"] = mini

    entries = mini.get("list")
    if not isinstance(entries, list):
        entries = []
        mini["list"] = entries

    existing = next((item for item in entries if isinstance(item, dict) and item.get("name") == compile_mode_name), None)
    if existing:
        existing["pathName"] = diagnostics_page
        existing["query"] = diagnostics_query
    else:
        entries.append({
            "id": -1,
            "name": compile_mode_name,
            "pathName": diagnostics_page,
            "query": diagnostics_query
        })

    project_config_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return "updated"


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).expanduser().resolve()
    diagnostics_route = f"/{args.diagnostics_page}?{args.diagnostics_query}"
    default_functions = [item.strip() for item in args.functions.split(",") if item.strip()]
    functions_json = json.dumps(default_functions, ensure_ascii=False)

    files = [
        (project_dir / "utils/devAutomationConfig.js", DEV_AUTOMATION_CONFIG.format(
            devtools_port=args.devtools_port,
            env_id=args.env_id,
            functions=functions_json,
            compile_mode_name=args.compile_mode_name
        ), False),
        (project_dir / "utils/devLaunchConfig.js", DEV_LAUNCH_CONFIG, False),
        (project_dir / "utils/generatedDevLaunchConfig.js", GENERATED_DEV_LAUNCH_CONFIG, False),
        (project_dir / "scripts/wechat-cli.sh", CLI_WRAPPER, True),
        (project_dir / "scripts/wechat-gui-compile.sh", GUI_COMPILE, True),
        (project_dir / "scripts/wechat-gui-refresh.sh", GUI_REFRESH, True),
        (project_dir / "scripts/wechat-gui-capture.sh", GUI_CAPTURE, True),
        (project_dir / "scripts/wechat-set-compile-mode.js", COMPILE_MODE_JS, False),
        (project_dir / "scripts/wechat-regression.sh", REGRESSION_SH.replace("__DIAGNOSTICS_ROUTE__", diagnostics_route), True),
    ]

    print(f"[bootstrap] project_dir={project_dir}")
    for path, content, executable in files:
        status = write_file(path, content, executable, args.force)
        print(f"[bootstrap] {status}: {path.relative_to(project_dir)}")

    compile_mode_status = ensure_compile_mode(
        project_dir / "project.config.json",
        args.compile_mode_name,
        args.diagnostics_page,
        args.diagnostics_query
    )
    print(f"[bootstrap] compile-mode: {compile_mode_status}")

    print("[bootstrap] next steps:")
    print(f"- add a diagnostics page at {args.diagnostics_page}")
    print("- add guarded diagnostics cloud functions before exposing global data")
    print("- statically import utils/devLaunchConfig.js in app.js or a page entry as fallback only")
    print("- run: scripts/wechat-cli.sh islogin")
    print("- run: node scripts/wechat-set-compile-mode.js")
    print("- run: scripts/wechat-regression.sh --skip-deploy --capture-delay 10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
