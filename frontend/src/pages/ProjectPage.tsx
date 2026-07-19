import { useEffect, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import {
  api,
  ApiError,
  type EnergyAssessment,
  type PowerCurve,
  type Project,
  type TurbinePosition,
} from "../api";
import { useAuth } from "../auth";

export function ProjectPage() {
  const { projectId = "" } = useParams();
  const { logout, user } = useAuth();
  const [project, setProject] = useState<Project | null>(null);
  const [turbines, setTurbines] = useState<TurbinePosition[]>([]);
  const [curves, setCurves] = useState<PowerCurve[]>([]);
  const [assessments, setAssessments] = useState<EnergyAssessment[]>([]);
  const [name, setName] = useState("Preliminary AEP");
  const [curveId, setCurveId] = useState("");
  const [ws, setWs] = useState("10");
  const [hours, setHours] = useState("8760");
  const [wake, setWake] = useState("0.1");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [latest, setLatest] = useState<EnergyAssessment | null>(null);

  async function refresh() {
    const [p, t, c, a] = await Promise.all([
      api.project(projectId),
      api.turbines(projectId),
      api.powerCurves(),
      api.assessments(projectId),
    ]);
    setProject(p);
    setTurbines(t);
    setCurves(c);
    setAssessments(a);
    if (!curveId && c[0]) setCurveId(c[0].id);
  }

  useEffect(() => {
    refresh().catch((err) =>
      setError(err instanceof ApiError ? err.message : "Failed to load project"),
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  async function runAssessment(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const created = await api.createAssessment(projectId, {
        name: name.trim() || "Preliminary AEP",
        power_curve: curveId,
        wind_distribution: [{ ws_m_s: Number(ws), hours: Number(hours) }],
        wake_loss_fraction: Number(wake),
      });
      setLatest(created);
      setAssessments(await api.assessments(projectId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Assessment failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="brand compact">Wind Platform</p>
          <p className="muted small">
            <Link to="/">All projects</Link>
            {project ? ` · ${project.name}` : null}
          </p>
        </div>
        <div className="topbar-actions">
          <span className="muted small">{user?.username}</span>
          <button type="button" className="ghost" onClick={() => void logout()}>
            Sign out
          </button>
        </div>
      </header>

      <main className="content">
        <section className="block">
          <h1>{project?.name ?? "Project"}</h1>
          <p className="lede">
            Review layout turbines and run a preliminary gross/net AEP using an existing power
            curve.{" "}
            <Link to={`/projects/${projectId}/layout`}>Open layout map →</Link>
          </p>
          {error ? <p className="error">{error}</p> : null}
        </section>

        <section className="split">
          <div className="block">
            <h2>Turbines ({turbines.length})</h2>
            {turbines.length ? (
              <ul className="list dense">
                {turbines.map((t) => (
                  <li key={t.id}>
                    <strong>{t.label}</strong>
                    <span className="muted">
                      {" "}
                      ({t.x.toFixed(1)}, {t.y.toFixed(1)})
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">
                No turbine positions yet. Import via API (`…/turbines/`) or Django admin, then
                refresh.
              </p>
            )}
          </div>

          <div className="block">
            <h2>Run AEP</h2>
            {!curves.length ? (
              <p className="muted">
                No power curves available. Create one via API (`/api/v1/energy/power-curves/`) and
                import CSV points first.
              </p>
            ) : (
              <form className="stack" onSubmit={runAssessment}>
                <label>
                  Assessment name
                  <input value={name} onChange={(e) => setName(e.target.value)} required />
                </label>
                <label>
                  Power curve
                  <select
                    value={curveId}
                    onChange={(e) => setCurveId(e.target.value)}
                    required
                  >
                    {curves.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name} ({c.points.length} pts)
                      </option>
                    ))}
                  </select>
                </label>
                <div className="row">
                  <label>
                    Wind speed (m/s)
                    <input
                      type="number"
                      step="0.1"
                      value={ws}
                      onChange={(e) => setWs(e.target.value)}
                      required
                    />
                  </label>
                  <label>
                    Hours
                    <input
                      type="number"
                      step="1"
                      value={hours}
                      onChange={(e) => setHours(e.target.value)}
                      required
                    />
                  </label>
                  <label>
                    Wake loss
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="0.5"
                      value={wake}
                      onChange={(e) => setWake(e.target.value)}
                      required
                    />
                  </label>
                </div>
                <button type="submit" disabled={busy || !curveId}>
                  {busy ? "Calculating…" : "Calculate gross energy"}
                </button>
              </form>
            )}

            {latest?.results?.plant_net_aep_mwh != null ? (
              <div className="result">
                <p className="result-label">Latest plant net AEP</p>
                <p className="result-value">
                  {latest.results.plant_net_aep_mwh.toLocaleString(undefined, {
                    maximumFractionDigits: 1,
                  })}{" "}
                  MWh
                </p>
                <p className="muted small">
                  Method {latest.results.method_version ?? latest.method_version} · turbines{" "}
                  {latest.results.turbine_count ?? "—"}
                </p>
              </div>
            ) : null}
          </div>
        </section>

        <section className="block">
          <h2>Previous assessments</h2>
          {assessments.length ? (
            <ul className="list">
              {assessments.map((a) => (
                <li key={a.id}>
                  <strong>{a.name}</strong>
                  <span className="muted">
                    {" "}
                    —{" "}
                    {a.results?.plant_net_aep_mwh != null
                      ? `${a.results.plant_net_aep_mwh.toLocaleString(undefined, {
                          maximumFractionDigits: 1,
                        })} MWh net`
                      : "no results"}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="muted">No assessments yet.</p>
          )}
        </section>
      </main>
    </div>
  );
}
