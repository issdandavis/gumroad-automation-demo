diff --git a/README.md b/README.md
index eb2a6d34c67ba371fb0287f3065af77a23c58ee6..829acd0632274ca5bc4cb0af6a01843c6fd85676 100644
--- a/README.md
+++ b/README.md
@@ -26,50 +26,51 @@ This repository features AI-powered automation for inter-account communications
 - **NEW:** AI-powered inbox management with auto-replies
 - **NEW:** Enterprise functions monitoring and validation
 
 **🆕 Inbox Management:**
 - ✅ **Auto-replies** to all GitHub notifications within 30 seconds
 - ✅ **Smart categorization** of issues, PRs, and discussions
 - ✅ **Multi-account support** for GitHub, GitLab, Bitbucket
 - ✅ **Email integration** ready (setup required)
 - ✅ **5 AI agents** working 24/7 to manage your inbox
 
 **🏢 Enterprise Monitoring (NEW):**
 - ✅ **Automated validation** every 4 hours of all enterprise functions
 - ✅ **AI-powered confirmation** that all systems are operational
 - ✅ **Health reports** with detailed analysis and recommendations
 - ✅ **Multi-platform monitoring** (GitHub, GitLab, Bitbucket, 2FA)
 - ✅ **Security validation** and integration status
 
 **Quick Start Guides:**
 - **[AI Employees Guide](docs/AI_EMPLOYEES_GUIDE.md)** - 5-minute setup for inbox management
 - **[Inbox Management](docs/INBOX_MANAGEMENT.md)** - Complete documentation
 - **[Enterprise Monitoring](docs/ENTERPRISE_MONITORING.md)** - Enterprise functions validation
 
 **Documentation:**
 - **[ACCOUNTS_README.md](ACCOUNTS_README.md)** - Complete account automation setup guide
 - **[docs/AUTOMATION_GUIDE.md](docs/AUTOMATION_GUIDE.md)** - Integration workflows
+- **[docs/pipedream_team_setup_workflows.md](docs/pipedream_team_setup_workflows.md)** - Two Pipedream flows for team onboarding and daily ops digests
 - **Configuration:** `config/automation-settings.json`, `config/enterprise-settings.json`
 
 ## Security
 Previous commits contained plaintext API keys. They have been removed from the tracked files. Make sure to rotate any keys that may have been exposed and only store live credentials in your local `.env` file. All automation credentials are stored securely in GitHub Secrets.
 # 🎮 Polly's Wingscroll: The First Thread
 
 **A choice-based narrative game set in Avalon Academy**
 
 ![Version](https://img.shields.io/badge/version-1.0-blue) ![Word Count](https://img.shields.io/badge/words-40000%2B-green) ![Endings](https://img.shields.io/badge/endings-14-purple)
 
 ---
 
 ## 🎯 Quick Start - PLAY NOW!
 
 ### Option 1: Instant Play (HTML Version)
 **👉 Just open `game/index.html` in your browser - that's it!**
 
 ### Option 2: ChoiceScript Version (Professional)
 See **[PLAY_THE_GAME.md](PLAY_THE_GAME.md)** for detailed instructions.
 
 ---
 
 ## 🤖 NEW: AI Autonomous Development System
 
 **Game development on autopilot!**
diff --git a/docs/pipedream_team_setup_workflows.md b/docs/pipedream_team_setup_workflows.md
new file mode 100644
index 0000000000000000000000000000000000000000..6ff5aeac2b361f0c3e79787ba9d40707c4be2ad1
--- /dev/null
+++ b/docs/pipedream_team_setup_workflows.md
@@ -0,0 +1,293 @@
+# Pipedream Workflows: Team Onboarding & Ops Digests
+
+This guide gives you two drop-in Pipedream workflows to stand up your teams fast and keep them aligned. Each flow uses only native Pipedream steps plus small Node.js code blocks you can paste directly into the editor. If you prefer **Zapier**, see the "Zapier equivalents" callouts for how to mirror the same logic with Webhooks, Storage, Slack, GitHub, and Notion actions.
+
+## Five-minute setup (do this once)
+1. Sign in to **Pipedream** and create a **Data Store** named from `PD_DATASTORE` (e.g., `team_setup_store`).
+2. Open **Settings → Secrets** and add the environment variables listed below.
+3. Click **New Workflow → HTTP / Webhook** and name it **Team Intake & Provisioning**.
+4. Paste the code blocks from the intake workflow in the order shown (Parse Intake → GitHub → Slack → Notion → Email → Response).
+5. Create another workflow **New Workflow → Scheduled** and name it **Daily Team Ops Digest**.
+6. Paste the digest steps (GitHub Activity → Linear [optional] → Data Store onboarding → Slack Digest → Guard) and set the cron.
+7. Send a sample payload to the intake webhook and run the digest once manually to confirm Slack + GitHub permissions.
+
+## Environment variables / secrets
+Set these in Pipedream (Secrets or Environment Variables):
+
+- `GITHUB_TOKEN` – classic/Pat with `admin:org` + `repo` for team provisioning
+- `SLACK_BOT_TOKEN` – bot token with `channels:manage`, `chat:write`, `users:read.email`
+- `NOTION_API_KEY` – Notion integration token with database write access (optional but recommended)
+- `NOTION_DB_ID` – Notion database ID to log team members
+- `WELCOME_EMAIL_FROM` – From address for welcome emails
+- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` – for SMTP send step (or swap with SendGrid/Mailgun action)
+- `STANDUP_SLACK_CHANNEL` – channel ID for digests (e.g., `C0123456789`)
+- `LINEAR_API_KEY` – optional; include if you want Linear ticket stats in the digest
+- `PD_DATASTORE` – name of a Pipedream Data Store for idempotency (e.g., `team_setup_store`)
+
+---
+
+## Workflow 1: "Team Intake & Provisioning"
+Use this to turn a form submission or Slack slash command into a fully provisioned teammate (GitHub team membership, Slack channel, Notion log, welcome email).
+
+### Trigger
+- **HTTP**: Accept JSON from a form tool (e.g., Tally/Typeform/Slack command)
+- **Expected payload**: `{ "email": "", "name": "", "github": "", "team": "", "role": "" }`
+
+### Step 1: Parse + dedupe request
+Add a **Node.js (Code)** step to normalize payloads and prevent double-runs using a Data Store.
+```javascript
+// Component name: parse_intake
+import { v4 as uuid } from "uuid";
+
+export default defineComponent({
+  props: {
+    datastore: { type: "app", app: "pipedream_data_store" },
+  },
+  async run({ steps, $ }) {
+    const body = steps.trigger?.event?.body || steps.trigger?.event || {};
+    const required = ["email", "name", "team"];
+    for (const key of required) {
+      if (!body[key]) throw new Error(`Missing field: ${key}`);
+    }
+
+    const ds = this.datastore;
+    const key = `intake:${body.email}`;
+    if (await ds.get(key)) {
+      $.export("status", "duplicate");
+      return body;
+    }
+    await ds.put(key, { id: uuid(), at: Date.now(), payload: body });
+    $.export("status", "new");
+    return body;
+  }
+});
+```
+
+### Step 2: Create/ensure GitHub team & membership
+Use a **Node.js (Code)** step. Keep it simple and additive; no try/catch on imports.
+```javascript
+// Component name: provision_github
+import axios from "axios";
+
+export default defineComponent({
+  async run({ steps, $ }) {
+    const gh = axios.create({
+      baseURL: "https://api.github.com",
+      headers: { Authorization: `token ${process.env.GITHUB_TOKEN}` }
+    });
+
+    const { team, github } = steps.parse_intake;
+    const org = "issdandavis"; // change if needed
+
+    // Ensure team exists (idempotent)
+    const teamRes = await gh.post(`/orgs/${org}/teams`, {
+      name: team,
+      privacy: "closed"
+    }).catch(async (err) => {
+      if (err.response?.status === 422) {
+        const existing = await gh.get(`/orgs/${org}/teams/${team}`);
+        return existing;
+      }
+      throw err;
+    });
+
+    const slug = teamRes.data?.slug || team;
+    // Add member
+    await gh.put(`/orgs/${org}/teams/${slug}/memberships/${github}`, {
+      role: "member"
+    });
+
+    $.export("team_slug", slug);
+  }
+});
+```
+
+### Step 3: Create/ensure Slack channel and invite user
+Use the built-in Slack app action or a small code step.
+```javascript
+// Component name: slack_channel_invite
+import axios from "axios";
+
+export default defineComponent({
+  async run({ steps, $ }) {
+    const slack = axios.create({
+      baseURL: "https://slack.com/api",
+      headers: { Authorization: `Bearer ${process.env.SLACK_BOT_TOKEN}` }
+    });
+
+    const { team, email } = steps.parse_intake;
+    const channelName = team.toLowerCase().replace(/\s+/g, "-");
+
+    // Ensure channel
+    const create = await slack.post("/conversations.create", { name: channelName }).catch((err) => err.response);
+    const channel = create?.data?.channel?.id || create?.data?.error === "name_taken" && (await slack.get("/conversations.list"))?.data?.channels?.find(c => c.name === channelName)?.id;
+
+    if (!channel) throw new Error("Unable to find or create channel");
+
+    // Invite by email (works if Slack has directory info)
+    const users = await slack.get("/users.lookupByEmail", { params: { email } }).catch(() => ({ data: {} }));
+    const userId = users.data?.user?.id;
+    if (userId) {
+      await slack.post("/conversations.invite", { channel, users: userId });
+    }
+
+    $.export("channel_id", channel);
+  }
+});
+```
+
+### Step 4: Log to Notion (optional)
+Add the Notion "Create Database Item" action or use a code step with `NOTION_API_KEY` and `NOTION_DB_ID`.
+
+### Step 5: Send welcome email
+Use the SMTP action with the parsed payload to send a templated welcome message. Include links to GitHub repos, Slack channel, and onboarding docs.
+
+### Step 6: Post confirmation back to requester
+Use a Slack chat.postMessage or HTTP response step to confirm provisioning.
+
+#### Zapier equivalent (overview)
+- **Trigger**: "Catch Hook" from Webhooks by Zapier.
+- **Parse + dedupe**: Use a Code step with "Storage by Zapier" (set key `intake:{email}`) to bail if already processed.
+- **GitHub provisioning**: "GitHub - Add Repository Collaborator" or "Add Team Member" actions; set defaults through labels/teams.
+- **Slack**: "Find User by Email" then "Invite User to Channel" (or "Create Channel" + invite).
+- **Notion / email**: Use the Notion "Create Database Item" and "SMTP by Zapier" actions with the parsed payload.
+
+##### Step-by-step Zapier setup
+If you want a direct webhook into your own app instead of the Pipedream flow, you can stand up a Zapier POST in a minute:
+
+1. In Zapier, create a new **Zap** and add an **Action → Webhooks by Zapier → POST**.
+2. Set the **URL** to your app endpoint: `https://your-app.replit.app/api/zapier/trigger` (replace `your-app` with the actual app name).
+3. In the **Data** section, paste a JSON body and fill in the values:
+
+   ```json
+   {
+     "projectId": "PROJECT_ID_HERE",
+     "goal": "WHAT_YOU_WANT_THE_AI_TO_DO",
+     "provider": "gemini"
+   }
+   ```
+
+   Example with real values:
+
+   ```json
+   {
+     "projectId": "abc123xyz",
+     "goal": "Analyze this customer feedback: {{feedback_text}}",
+     "provider": "gemini"
+   }
+   ```
+
+4. Test the step in Zapier; it returns a `runId` your next step can use.
+
+Once the test passes, publish the Zap.
+
+---
+
+## Workflow 2: "Daily Team Ops Digest"
+Send a single Slack digest with the latest GitHub, Linear, and onboarding status so teams stay aligned.
+
+### Trigger
+- **Scheduled**: e.g., cron `0 15 * * *` (15:00 UTC)
+
+### Step 1: Fetch GitHub activity for the team
+```javascript
+// Component name: github_activity
+import axios from "axios";
+
+export default defineComponent({
+  async run({ steps, $ }) {
+    const org = "issdandavis"; // change to your org
+    const teams = ["core", "writers", "qa"]; // keep in sync with Team Intake flow
+    const gh = axios.create({
+      baseURL: "https://api.github.com",
+      headers: { Authorization: `token ${process.env.GITHUB_TOKEN}` }
+    });
+
+    const since = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
+    const repos = (await gh.get(`/orgs/${org}/repos`)).data || [];
+
+    const byTeam = {};
+    for (const team of teams) {
+      byTeam[team] = [];
+    }
+
+    for (const repo of repos) {
+      const prs = (await gh.get(`/repos/${org}/${repo.name}/pulls`, { params: { state: "open", sort: "updated", direction: "desc" } })).data;
+      const issues = (await gh.get(`/repos/${org}/${repo.name}/issues`, { params: { state: "open", since } })).data;
+      for (const item of [...prs, ...issues]) {
+        const labelTeams = (item.labels || []).map((l) => l.name).filter((n) => teams.includes(n));
+        for (const t of labelTeams) byTeam[t].push({ title: item.title, url: item.html_url, updated_at: item.updated_at, type: item.pull_request ? "PR" : "Issue" });
+      }
+    }
+
+    $.export("byTeam", byTeam);
+  }
+});
+```
+
+### Step 2: Pull Linear ticket summary (optional)
+If `LINEAR_API_KEY` is set, add a Node.js step using the Linear GraphQL endpoint to fetch `status:In Progress` + `Blocked` counts per team label.
+
+### Step 3: Add onboarding completions from Data Store
+Re-use the same Data Store from the intake flow to show yesterday's new teammates and their channels.
+
+### Step 4: Compose Slack message
+```javascript
+// Component name: slack_digest
+import axios from "axios";
+
+export default defineComponent({
+  async run({ steps, $ }) {
+    const byTeam = steps.github_activity.byTeam;
+    const slack = axios.create({
+      baseURL: "https://slack.com/api",
+      headers: { Authorization: `Bearer ${process.env.SLACK_BOT_TOKEN}` }
+    });
+
+    const lines = ["*Daily Team Ops Digest*", ""]; 
+    for (const [team, items] of Object.entries(byTeam)) {
+      lines.push(`*${team.toUpperCase()}*`);
+      if (!items.length) { lines.push("- No updates in the last 24h"); continue; }
+      for (const item of items.slice(0, 10)) {
+        lines.push(`- ${item.type}: <${item.url}|${item.title}> (updated ${new Date(item.updated_at).toLocaleString()})`);
+      }
+      lines.push("");
+    }
+
+    await slack.post("/chat.postMessage", {
+      channel: process.env.STANDUP_SLACK_CHANNEL,
+      text: lines.join("\n")
+    });
+  }
+});
+```
+
+### Step 5: Safety guard
+Add a short code step that exits early if no activity was collected (prevents sending empty digests) or if the same digest already ran (use Data Store key `digest:<date>`).
+
+#### Zapier equivalent (overview)
+- **Trigger**: "Schedule by Zapier" set to your preferred time.
+- **GitHub activity**: Use "GitHub - Find Issue" and "Find Pull Request" with filters per label; aggregate with a Code step.
+- **Linear**: Call the GraphQL API from a Webhooks by Zapier "Custom Request" step if the API key is present.
+- **Onboarding completions**: Pull from the same "Storage by Zapier" entries that were written during intake.
+- **Slack digest**: "Slack - Send Channel Message" with the composed text; add a Storage guard key `digest:{date}` to prevent duplicates.
+
+---
+
+## Quick setup checklist
+1. Create a new Pipedream workflow named **Team Intake & Provisioning**
+   - Trigger: HTTP
+   - Steps: Parse Intake → GitHub Provisioning → Slack Channel Invite → Notion log (optional) → SMTP welcome → Respond
+2. Create another workflow **Daily Team Ops Digest**
+   - Trigger: Scheduled cron
+   - Steps: GitHub Activity → (Optional) Linear Summary → Data Store onboarding → Slack Digest → Guard
+3. Add required secrets/environment variables.
+4. Test with a sample payload and a private Slack channel before inviting the full team.
+
+## Operational tips
+- Use Pipedream's **Data Store** to enforce idempotency for both flows.
+- Keep team names consistent between GitHub labels and Slack channel names so the digest mapping works.
+- For large orgs, narrow GitHub API calls by repository list rather than fetching all repos each run.
+- If email is handled elsewhere, swap the SMTP step with a webhook to your provider.
+
+These two workflows cover the core lifecycle: getting teammates set up quickly and keeping them informed every day.
