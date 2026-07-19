import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import {
  api,
  ApiError,
  type Project,
  type TurbineModel,
  type TurbinePosition,
} from "../api";
import { useAuth } from "../auth";
import { LayoutMap } from "../components/LayoutMap";

export function LayoutPage() {
  const { projectId = "" } = useParams();
  const { logout, user } = useAuth();
  const [project, setProject] = useState<Project | null>(null);
  const [turbines, setTurbines] = useState<TurbinePosition[]>([]);
  const [models, setModels] = useState<TurbineModel[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  const [label, setLabel] = useState("");
  const [x, setX] = useState("0");
  const [y, setY] = useState("0");
  const [modelId, setModelId] = useState("");

  const [mfr, setMfr] = useState("");
  const [modelName, setModelName] = useState("");
  const [hh, setHh] = useState("100");
  const [rd, setRd] = useState("120");
  const [rated, setRated] = useState("3000");
  const [pcFile, setPcFile] = useState<File | null>(null);
  const [ctFile, setCtFile] = useState<File | null>(null);

  const selected = turbines.find((t) => t.id === selectedId) ?? null;

  const refresh = useCallback(async () => {
    const [p, t, m] = await Promise.all([
      api.project(projectId),
      api.turbines(projectId),
      api.turbineModels(),
    ]);
    setProject(p);
    setTurbines(t);
    setModels(m);
    if (!modelId && m[0]) setModelId(m[0].id);
  }, [projectId, modelId]);

  useEffect(() => {
    refresh().catch((err) =>
      setError(err instanceof ApiError ? err.message : "Failed to load layout"),
    );
  }, [refresh]);

  useEffect(() => {
    if (!selected) return;
    setLabel(selected.label);
    setX(String(selected.x));
    setY(String(selected.y));
    setModelId(selected.turbine_model || modelId);
  }, [selected, modelId]);

  async function addTurbine(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setInfo(null);
    try {
      await api.createTurbine(projectId, {
        label: label.trim(),
        x: Number(x),
        y: Number(y),
        turbine_model: modelId,
      });
      setLabel("");
      await refresh();
      setInfo("Turbine added.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not add turbine");
    }
  }

  async function saveSelected(e: FormEvent) {
    e.preventDefault();
    if (!selected) return;
    setError(null);
    try {
      await api.updateTurbine(projectId, selected.id, {
        label: label.trim(),
        x: Number(x),
        y: Number(y),
        turbine_model: modelId || null,
      });
      await refresh();
      setInfo("Turbine updated.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not update turbine");
    }
  }

  async function removeSelected() {
    if (!selected) return;
    setError(null);
    try {
      await api.deleteTurbine(projectId, selected.id);
      setSelectedId(null);
      await refresh();
      setInfo("Turbine deleted.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not delete turbine");
    }
  }

  async function onImportPositions(file: File | null) {
    if (!file) return;
    setError(null);
    try {
      const result = await api.importTurbines(projectId, file);
      await refresh();
      setInfo(`Import: ${result.created} created, ${result.updated} updated.`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Import failed");
    }
  }

  async function onImportCatalogue(file: File | null) {
    if (!file) return;
    setError(null);
    try {
      const result = await api.importCatalogue(file);
      setModels(await api.turbineModels());
      setInfo(`Catalogue: ${result.created} created, ${result.updated} updated.`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Catalogue import failed");
    }
  }

  async function createModelWithCurves(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setInfo(null);
    try {
      const model = await api.createTurbineModel({
        manufacturer_name_write: mfr.trim(),
        name: modelName.trim(),
        hub_height_m: Number(hh),
        rotor_diameter_m: Number(rd),
        rated_power_kw: Number(rated),
      });
      if (pcFile) {
        const pc = await api.createPowerCurve({
          turbine_model: model.id,
          name: `${model.name} power`,
        });
        await api.importPowerCurve(pc.id, pcFile);
      }
      if (ctFile) {
        const ct = await api.createCtCurve({
          turbine_model: model.id,
          name: `${model.name} Ct`,
        });
        await api.importCtCurve(ct.id, ctFile);
      }
      setModels(await api.turbineModels());
      setModelId(model.id);
      setMfr("");
      setModelName("");
      setPcFile(null);
      setCtFile(null);
      setInfo(`Model ${model.manufacturer_name} ${model.name} created.`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create model");
    }
  }

  const onMove = useCallback(
    (id: string, nx: number, ny: number) => {
      void (async () => {
        try {
          await api.updateTurbine(projectId, id, { x: nx, y: ny });
          setTurbines(await api.turbines(projectId));
          setInfo("Coordinates updated from map.");
        } catch (err) {
          setError(err instanceof ApiError ? err.message : "Map update failed");
        }
      })();
    },
    [projectId],
  );

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="brand compact">Wind Platform</p>
          <p className="muted small">
            <Link to="/">Projects</Link>
            {" · "}
            <Link to={`/projects/${projectId}`}>{project?.name ?? "Project"}</Link>
            {" · Layout"}
          </p>
        </div>
        <div className="topbar-actions">
          <span className="muted small">{user?.username}</span>
          <button type="button" className="ghost" onClick={() => void logout()}>
            Sign out
          </button>
        </div>
      </header>

      <main className="content layout-page">
        <section className="block">
          <h1>Layout — {project?.name ?? "…"}</h1>
          <p className="lede">
            Add or import turbines, assign catalogue models, edit coordinates on the map
            (planar project CRS). Create missing models with power and Ct curves.
          </p>
          {error ? <p className="error">{error}</p> : null}
          {info ? <p className="muted">{info}</p> : null}
        </section>

        <section className="layout-grid">
          <div className="block map-block">
            <h2>Map</h2>
            <LayoutMap
              turbines={turbines}
              selectedId={selectedId}
              onSelect={setSelectedId}
              onMove={onMove}
            />
            <p className="muted small">Drag a marker to update x/y. Click to select.</p>
          </div>

          <div className="block">
            <h2>Turbines ({turbines.length})</h2>
            <ul className="list dense">
              {turbines.map((t) => (
                <li key={t.id}>
                  <button
                    type="button"
                    className={selectedId === t.id ? "ghost selected" : "ghost"}
                    onClick={() => setSelectedId(t.id)}
                  >
                    {t.label}
                  </button>
                  <span className="muted small">
                    {" "}
                    ({t.x.toFixed(1)}, {t.y.toFixed(1)}){" "}
                    {t.turbine_model_name ?? "no model"}
                  </span>
                </li>
              ))}
              {!turbines.length ? <li className="muted">No turbines yet.</li> : null}
            </ul>

            <form className="stack" onSubmit={selected ? saveSelected : addTurbine}>
              <label>
                Label
                <input value={label} onChange={(e) => setLabel(e.target.value)} required />
              </label>
              <div className="row">
                <label>
                  X
                  <input value={x} onChange={(e) => setX(e.target.value)} required />
                </label>
                <label>
                  Y
                  <input value={y} onChange={(e) => setY(e.target.value)} required />
                </label>
              </div>
              <label>
                Turbine model
                <select value={modelId} onChange={(e) => setModelId(e.target.value)} required>
                  {!models.length ? <option value="">No models — create below</option> : null}
                  {models.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.manufacturer_name} {m.name} ({m.rated_power_kw} kW)
                    </option>
                  ))}
                </select>
              </label>
              <div className="inline-form">
                <button type="submit">{selected ? "Save changes" : "Add turbine"}</button>
                {selected ? (
                  <button type="button" className="ghost" onClick={() => void removeSelected()}>
                    Delete
                  </button>
                ) : null}
              </div>
            </form>

            <h2>Import positions CSV</h2>
            <p className="muted small">
              Columns: label,x,y[,z][,manufacturer,model]
            </p>
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={(e) => void onImportPositions(e.target.files?.[0] ?? null)}
            />

            <h2>Import catalogue CSV</h2>
            <p className="muted small">
              manufacturer,model,hub_height_m,rotor_diameter_m,rated_power_kw
            </p>
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={(e) => void onImportCatalogue(e.target.files?.[0] ?? null)}
            />
          </div>
        </section>

        <section className="block">
          <h2>Create turbine model (+ curves)</h2>
          <form className="stack" onSubmit={createModelWithCurves}>
            <div className="row">
              <label>
                Manufacturer
                <input value={mfr} onChange={(e) => setMfr(e.target.value)} required />
              </label>
              <label>
                Model name
                <input
                  value={modelName}
                  onChange={(e) => setModelName(e.target.value)}
                  required
                />
              </label>
            </div>
            <div className="row">
              <label>
                Hub height (m)
                <input value={hh} onChange={(e) => setHh(e.target.value)} required />
              </label>
              <label>
                Rotor diameter (m)
                <input value={rd} onChange={(e) => setRd(e.target.value)} required />
              </label>
              <label>
                Rated power (kW)
                <input value={rated} onChange={(e) => setRated(e.target.value)} required />
              </label>
            </div>
            <div className="row">
              <label>
                Power curve CSV (ws_m_s,power_kw)
                <input
                  type="file"
                  accept=".csv,text/csv"
                  onChange={(e) => setPcFile(e.target.files?.[0] ?? null)}
                />
              </label>
              <label>
                Ct curve CSV (ws_m_s,ct)
                <input
                  type="file"
                  accept=".csv,text/csv"
                  onChange={(e) => setCtFile(e.target.files?.[0] ?? null)}
                />
              </label>
            </div>
            <button type="submit">Create model</button>
          </form>
        </section>
      </main>
    </div>
  );
}
