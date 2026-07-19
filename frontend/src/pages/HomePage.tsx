import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import {
  api,
  ApiError,
  type Organization,
  type Project,
} from "../api";
import { useAuth } from "../auth";

export function HomePage() {
  const { user, logout } = useAuth();
  const [orgs, setOrgs] = useState<Organization[]>([]);
  const [selectedOrg, setSelectedOrg] = useState<string>("");
  const [projects, setProjects] = useState<Project[]>([]);
  const [orgName, setOrgName] = useState("");
  const [projectName, setProjectName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function refreshOrgs(preferId?: string) {
    const list = await api.organizations();
    setOrgs(list);
    const next = preferId || selectedOrg || list[0]?.id || "";
    setSelectedOrg(next);
    return next;
  }

  useEffect(() => {
    refreshOrgs()
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Failed to load organizations"),
      )
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!selectedOrg) {
      setProjects([]);
      return;
    }
    api
      .projects(selectedOrg)
      .then(setProjects)
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Failed to load projects"),
      );
  }, [selectedOrg]);

  async function createOrg(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const org = await api.createOrganization(orgName.trim());
      setOrgName("");
      await refreshOrgs(org.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create organization");
    }
  }

  async function createProject(e: FormEvent) {
    e.preventDefault();
    if (!selectedOrg) return;
    setError(null);
    try {
      await api.createProject(selectedOrg, projectName.trim());
      setProjectName("");
      setProjects(await api.projects(selectedOrg));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create project");
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="brand compact">Wind Platform</p>
          <p className="muted small">Signed in as {user?.username}</p>
        </div>
        <button type="button" className="ghost" onClick={() => void logout()}>
          Sign out
        </button>
      </header>

      <main className="content">
        <section className="block">
          <h1>Organizations & projects</h1>
          <p className="lede">
            Pick a workspace, open a project, then run a preliminary AEP assessment.
          </p>
          {error ? <p className="error">{error}</p> : null}
          {loading ? <p className="muted">Loading…</p> : null}
        </section>

        <section className="split">
          <div className="block">
            <h2>Organizations</h2>
            <label>
              Active organization
              <select
                value={selectedOrg}
                onChange={(e) => setSelectedOrg(e.target.value)}
                disabled={!orgs.length}
              >
                {!orgs.length ? <option value="">No organizations yet</option> : null}
                {orgs.map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.name}
                  </option>
                ))}
              </select>
            </label>
            <form className="inline-form" onSubmit={createOrg}>
              <input
                placeholder="New organization name"
                value={orgName}
                onChange={(e) => setOrgName(e.target.value)}
                required
              />
              <button type="submit">Create</button>
            </form>
          </div>

          <div className="block">
            <h2>Projects</h2>
            {!selectedOrg ? (
              <p className="muted">Create an organization first.</p>
            ) : (
              <>
                <ul className="list">
                  {projects.map((p) => (
                    <li key={p.id}>
                      <Link to={`/projects/${p.id}`}>{p.name}</Link>
                    </li>
                  ))}
                  {!projects.length ? (
                    <li className="muted">No projects in this organization.</li>
                  ) : null}
                </ul>
                <form className="inline-form" onSubmit={createProject}>
                  <input
                    placeholder="New project name"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    required
                  />
                  <button type="submit">Create</button>
                </form>
              </>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
