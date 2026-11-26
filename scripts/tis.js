// Register, enable, disable or check the keyboard layouts of a bundle, using the
// Text Input Sources API from JavaScript for Automation (ships with every macOS).
//   osascript -l JavaScript tis.js enable|disable|status "/path/ModernMongolian.bundle"
// `status` fails unless every layout is enabled. Run it as a separate process after
// `enable`: a process does not see its own enable calls take effect right away.
ObjC.import("Carbon");
ObjC.bindFunction("TISCreateInputSourceList", ["id", ["id", "bool"]]);
ObjC.bindFunction("TISGetInputSourceProperty", ["id", ["id", "id"]]);
ObjC.bindFunction("TISRegisterInputSource", ["int", ["id"]]);
ObjC.bindFunction("TISEnableInputSource", ["int", ["id"]]);
ObjC.bindFunction("TISDisableInputSource", ["int", ["id"]]);

function layoutIDs(bundlePath) {
  const info = $.NSDictionary.dictionaryWithContentsOfFile(`${bundlePath}/Contents/Info.plist`);
  if (info.isNil()) throw new Error(`not a keyboard layout bundle: ${bundlePath}`);
  const plist = ObjC.deepUnwrap(info);
  return Object.keys(plist)
    .filter((key) => key.startsWith("KLInfo_"))
    .map((key) => plist[key].TISInputSourceID);
}

function findSource(id) {
  const list = $.TISCreateInputSourceList($({ TISPropertyInputSourceID: id }), true);
  return list.isNil() || list.count === 0 ? null : list.objectAtIndex(0);
}

function isEnabled(source) {
  // "TSMInputSourcePropertyIsEnabled" is the value of kTISPropertyInputSourceIsEnabled.
  const value = $.TISGetInputSourceProperty(source, $("TSMInputSourcePropertyIsEnabled"));
  return !value.isNil() && value.boolValue;
}

function run(argv) {
  const [action, bundlePath] = argv;
  if (!["enable", "disable", "status"].includes(action) || !bundlePath) {
    throw new Error("usage: tis.js enable|disable|status <bundle>");
  }
  if (action === "enable") {
    const status = $.TISRegisterInputSource($.NSURL.fileURLWithPath(bundlePath));
    if (status !== 0) throw new Error(`TISRegisterInputSource failed (${status})`);
  }
  const lines = [];
  for (const id of layoutIDs(bundlePath)) {
    const source = findSource(id);
    if (!source) {
      if (action === "disable") continue;
      throw new Error(`macOS does not see ${id}`);
    }
    if (action === "status") {
      if (!isEnabled(source)) throw new Error(`${id} is not enabled`);
      lines.push(`enabled ${id}`);
      continue;
    }
    const status = action === "enable" ? $.TISEnableInputSource(source) : $.TISDisableInputSource(source);
    if (status !== 0) throw new Error(`${action} ${id} failed (${status})`);
    lines.push(`${action}d ${id}`);
  }
  return lines.join("\n");
}
