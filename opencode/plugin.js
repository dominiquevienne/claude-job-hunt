import path from "node:path"
import { fileURLToPath } from "node:url"

// Resolve from this module rather than from OpenWork's current directory. The
// latter is the workspace, not necessarily the checkout containing this file.
const REPO_ROOT = path.resolve(fileURLToPath(new URL("../", import.meta.url)))
const SKILLS_PATH = path.join(REPO_ROOT, "skills")

const JOB_SETUP_COMMAND = {
  description: "Set up or change the job-hunt workspace",
  template: "Load the `job-setup` skill and follow its instructions.",
}

export const OpenWorkJobHuntPlugin = async () => ({
  config: async (cfg) => {
    cfg.skills ??= {}
    cfg.skills.paths ??= []
    if (!cfg.skills.paths.includes(SKILLS_PATH)) {
      cfg.skills.paths.push(SKILLS_PATH)
    }

    cfg.command ??= {}
    if (!Object.prototype.hasOwnProperty.call(cfg.command, "job-setup")) {
      cfg.command["job-setup"] = { ...JOB_SETUP_COMMAND }
    }
  },

  "shell.env": async (_input, output) => {
    output.env ??= {}
    output.env.JOB_HUNT_ROOT = REPO_ROOT
  },
})
