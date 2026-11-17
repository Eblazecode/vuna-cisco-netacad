import { useCallback, useEffect, useMemo, useState, type FormEvent, type ReactNode } from "react";
import {
  Activity, Award, Bell, BookOpen, Building2,
  CalendarCheck, CheckCircle2, ChevronDown, CircleHelp, ClipboardList, Clock3,
  CreditCard, FileText, GraduationCap, LayoutDashboard, LogOut, Menu, MoreHorizontal,
  Network, Plus, Search, Settings, ShieldCheck, Users, UserPlus, X, RefreshCw
} from "lucide-react";

type User = { id: string; email: string; first_name: string; last_name: string; role: string };
type Student = {
  id: string; matric_number: string; first_name: string; middle_name?: string;
  last_name: string; email: string; faculty_name?: string; department_name?: string;
  academic_level?: string; status: string; admission_year?: number;
};
type Faculty = { id: string; name: string; code: string };
type Department = { id: string; name: string; code: string; faculty_id: string };
type Programme = { id: string; name: string; code: string; department_id: string };
type PageResult<T> = { count: number; results: T[]; next?: string | null; previous?: string | null };
type View = "overview" | "students" | "faculties" | "registration" | "courses" | "attendance" | "results" | "finance" | "certifications" | "analytics" | "settings";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
const navigation: { id: View; label: string; icon: typeof LayoutDashboard; group: string }[] = [
  { id: "overview", label: "Overview", icon: LayoutDashboard, group: "Workspace" },
  { id: "students", label: "Student registry", icon: Users, group: "Workspace" },
  { id: "faculties", label: "Faculties & departments", icon: Building2, group: "Workspace" },
  { id: "courses", label: "Courses & programmes", icon: BookOpen, group: "Academy" },
  { id: "attendance", label: "Attendance", icon: CalendarCheck, group: "Academy" },
  { id: "results", label: "Assessments & results", icon: ClipboardList, group: "Academy" },
  { id: "finance", label: "Finance & payments", icon: CreditCard, group: "Administration" },
  { id: "certifications", label: "Certifications", icon: Award, group: "Administration" },
  { id: "analytics", label: "Analytics & reports", icon: Activity, group: "Administration" },
  { id: "settings", label: "System settings", icon: Settings, group: "Administration" },
];

function getStoredToken() { return sessionStorage.getItem("vuna_access"); }
function getStoredRefresh() { return sessionStorage.getItem("vuna_refresh"); }
function clearTokens() { sessionStorage.removeItem("vuna_access"); sessionStorage.removeItem("vuna_refresh"); }

async function apiRequest<T>(path: string, init: RequestInit = {}, token?: string | null): Promise<T> {
  if (!API_BASE) throw new Error("The API URL is not configured. Set VITE_API_BASE_URL in the deployment environment.");
  const makeRequest = (access: string | null) => fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...(init.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(access ? { Authorization: `Bearer ${access}` } : {}),
      ...init.headers,
    },
  });
  let response = await makeRequest(token ?? getStoredToken());
  if (response.status === 401 && getStoredRefresh() && path !== "/api/v1/auth/token/refresh/") {
    const refreshResponse = await fetch(`${API_BASE}/api/v1/auth/token/refresh/`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: getStoredRefresh() }),
    });
    if (refreshResponse.ok) {
      const refreshed = await refreshResponse.json();
      sessionStorage.setItem("vuna_access", refreshed.access);
      response = await makeRequest(refreshed.access);
    } else {
      clearTokens();
    }
  }
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload.detail || Object.entries(payload).map(([key, value]) =>
      `${key}: ${Array.isArray(value) ? value.join(", ") : String(value)}`).join(" · ");
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return payload as T;
}

function initials(user: User) {
  return `${user.first_name?.[0] || user.email[0]}${user.last_name?.[0] || ""}`.toUpperCase();
}
function displayRole(role: string) {
  return role.toLowerCase().split("_").map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
}
function statusClass(status: string) {
  return status.toLowerCase() === "active" ? "status-active" :
    status.toLowerCase() === "pending" ? "status-pending" : "status-muted";
}

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(getStoredToken());
  const [view, setView] = useState<View>("overview");
  const [authMode, setAuthMode] = useState<"login" | "registration">("login");
  const [loading, setLoading] = useState(Boolean(getStoredToken()));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [mobileNav, setMobileNav] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [students, setStudents] = useState<Student[]>([]);
  const [studentCount, setStudentCount] = useState<number | null>(null);
  const [pendingCount, setPendingCount] = useState<number | null>(null);
  const [facultyCount, setFacultyCount] = useState<number | null>(null);
  const [faculties, setFaculties] = useState<Faculty[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [programmes, setProgrammes] = useState<Programme[]>([]);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState({
    matric_number: "", first_name: "", middle_name: "", last_name: "", email: "",
    phone_number: "", faculty: "", department: "", programme: "", academic_level: "",
    admission_year: String(new Date().getFullYear()), password: "",
  });

  const loadUser = useCallback(async (access: string) => {
    const me = await apiRequest<User>("/api/v1/auth/me/", {}, access);
    setUser(me);
  }, []);

  const loadReferences = useCallback(async () => {
    const data = await apiRequest<{ faculties: Faculty[]; departments: Department[]; programmes: Programme[] }>(
      "/api/v1/public/academic-structure/", {}, null,
    );
    setFaculties(data.faculties);
    setDepartments(data.departments);
    setProgrammes(data.programmes);
  }, []);

  const loadDashboard = useCallback(async (access: string) => {
    const [all, pending, facultyResult] = await Promise.allSettled([
      apiRequest<PageResult<Student>>("/api/v1/students/?page=1", {}, access),
      apiRequest<PageResult<Student>>("/api/v1/students/?status=PENDING&page=1", {}, access),
      apiRequest<PageResult<Faculty>>("/api/v1/faculties/?page=1", {}, access),
    ]);
    if (all.status === "fulfilled") { setStudentCount(all.value.count); setStudents(all.value.results.slice(0, 7)); }
    if (pending.status === "fulfilled") setPendingCount(pending.value.count);
    if (facultyResult.status === "fulfilled") { setFacultyCount(facultyResult.value.count); setFaculties(facultyResult.value.results); }
  }, []);

  useEffect(() => {
    const existing = getStoredToken();
    if (!existing) { setLoading(false); return; }
    loadUser(existing)
      .then(() => loadDashboard(existing))
      .catch(() => { clearTokens(); setToken(null); setUser(null); })
      .finally(() => setLoading(false));
  }, [loadDashboard, loadUser]);

  useEffect(() => {
    if (authMode === "registration") loadReferences().catch((e) => setError(e.message));
  }, [authMode, loadReferences]);

  useEffect(() => {
    if (user && (view === "students" || view === "faculties")) {
      const path = view === "students"
        ? `/api/v1/students/?page=1${search ? `&q=${encodeURIComponent(search)}` : ""}`
        : "/api/v1/faculties/?page=1";
      apiRequest<PageResult<Student & Faculty>>(path, {}, token)
        .then((data) => { if (view === "students") { setStudents(data.results as Student[]); setStudentCount(data.count); } else { setFaculties(data.results as Faculty[]); setFacultyCount(data.count); } })
        .catch((e) => setError(e.message));
    }
  }, [user, view, search, token]);

  const submitLogin = async (event: FormEvent) => {
    event.preventDefault(); setBusy(true); setError("");
    try {
      const result = await apiRequest<{ access: string; refresh: string }>("/api/v1/auth/token/", {
        method: "POST", body: JSON.stringify({ email, password }),
      }, null);
      sessionStorage.setItem("vuna_access", result.access);
      sessionStorage.setItem("vuna_refresh", result.refresh);
      setToken(result.access);
      await loadUser(result.access);
      await loadDashboard(result.access);
      setView("overview");
    } catch (e) { setError(e instanceof Error ? e.message : "Unable to sign in."); }
    finally { setBusy(false); }
  };

  const submitRegistration = async (event: FormEvent) => {
    event.preventDefault(); setBusy(true); setError(""); setNotice("");
    try {
      await apiRequest("/api/v1/registration/", {
        method: "POST",
        body: JSON.stringify({
          ...form, admission_year: form.admission_year ? Number(form.admission_year) : null,
          faculty: form.faculty, department: form.department,
          programme: form.programme || null,
        }),
      }, null);
      setNotice("Your application has been submitted for verification. You can sign in after an authorised university officer approves your record.");
      setAuthMode("login");
      setPassword("");
    } catch (e) { setError(e instanceof Error ? e.message : "Registration could not be submitted."); }
    finally { setBusy(false); }
  };

  const submitAdminStudent = async (event: FormEvent) => {
    event.preventDefault(); setBusy(true); setError(""); setNotice("");
    try {
      await apiRequest("/api/v1/students/", {
        method: "POST",
        body: JSON.stringify({
          matric_number: form.matric_number, first_name: form.first_name,
          middle_name: form.middle_name, last_name: form.last_name, email: form.email,
          phone_number: form.phone_number, faculty: form.faculty, department: form.department,
          programme: form.programme || null, academic_level: form.academic_level,
          admission_year: form.admission_year ? Number(form.admission_year) : null,
        }),
      }, token);
      setNotice("Student record created and submitted for verification.");
      setForm({ ...form, matric_number: "", first_name: "", middle_name: "", last_name: "", email: "", phone_number: "" });
      setView("students");
      await loadDashboard(token || "");
    } catch (e) { setError(e instanceof Error ? e.message : "Student record could not be created."); }
    finally { setBusy(false); }
  };

  const signOut = () => { clearTokens(); setToken(null); setUser(null); setStudents([]); setView("overview"); };
  const activeNavigation = navigation.find((item) => item.id === view);
  const greeting = useMemo(() => user ? user.first_name || user.email.split("@")[0] : "there", [user]);

  if (loading) return <div className="loading-screen"><div className="brand-mark"><Network size={22}/></div><span>Loading VUNA workspace…</span></div>;

  if (!user) {
    return (
      <main className="auth-layout">
        <section className="auth-visual">
          <div className="auth-brand"><div className="brand-mark"><Network size={22}/></div><span>VUNA <b>Cisco NetAcad</b></span></div>
          <div className="auth-copy">
            <span className="eyebrow light">VERITAS UNIVERSITY · ABUJA</span>
            <h1>Building the next generation of <em>digital leaders.</em></h1>
            <p>A connected platform for student services, professional technology training and institutional intelligence.</p>
            <div className="auth-highlights">
              <div><ShieldCheck size={18}/><span>Secure student records</span></div>
              <div><GraduationCap size={18}/><span>Professional learning pathways</span></div>
              <div><Activity size={18}/><span>Insight-led administration</span></div>
            </div>
          </div>
          <div className="auth-footer">Veritas University Cisco Networking Academy <span>© {new Date().getFullYear()}</span></div>
        </section>
        <section className="auth-panel">
          <div className="auth-form-wrap">
            <div className="mobile-brand"><div className="brand-mark"><Network size={20}/></div><b>VUNA Cisco NetAcad</b></div>
            <span className="eyebrow">{authMode === "login" ? "WELCOME BACK" : "STUDENT ONBOARDING"}</span>
            <h2>{authMode === "login" ? "Sign in to your portal" : "Create your student profile"}</h2>
            <p className="muted">{authMode === "login" ? "Use your registered university or academy account." : "Submit your details for university record verification."}</p>
            {notice && <div className="success-message"><CheckCircle2 size={17}/>{notice}</div>}
            {error && <div className="error-message">{error}</div>}
            {authMode === "login" ? (
              <form onSubmit={submitLogin} className="form-stack">
                <label>Email address<input type="email" autoComplete="username" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="name@veritas.edu.ng"/></label>
                <label>Password<input type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter your password"/></label>
                <button className="primary-button full-button" disabled={busy}>{busy ? "Signing in…" : "Sign in"} <span>→</span></button>
              </form>
            ) : (
              <form onSubmit={submitRegistration} className="form-stack">
                <div className="form-grid">
                  <label>Matriculation number<input required value={form.matric_number} onChange={(e) => setForm({...form, matric_number:e.target.value})}/></label>
                  <label>First name<input required value={form.first_name} onChange={(e) => setForm({...form, first_name:e.target.value})}/></label>
                  <label>Middle name<input value={form.middle_name} onChange={(e) => setForm({...form, middle_name:e.target.value})}/></label>
                  <label>Last name<input required value={form.last_name} onChange={(e) => setForm({...form, last_name:e.target.value})}/></label>
                  <label>Email address<input type="email" required value={form.email} onChange={(e) => setForm({...form, email:e.target.value})}/></label>
                  <label>Phone number<input value={form.phone_number} onChange={(e) => setForm({...form, phone_number:e.target.value})}/></label>
                  <label>Faculty<select required value={form.faculty} onChange={(e) => setForm({...form, faculty:e.target.value, department:"", programme:""})}><option value="">Select faculty</option>{faculties.map(f=><option key={f.id} value={f.id}>{f.name}</option>)}</select></label>
                  <label>Department<select required value={form.department} onChange={(e) => setForm({...form, department:e.target.value, programme:""})}><option value="">Select department</option>{departments.filter(d=>d.faculty_id===form.faculty).map(d=><option key={d.id} value={d.id}>{d.name}</option>)}</select></label>
                  <label>Programme<select value={form.programme} onChange={(e) => setForm({...form, programme:e.target.value})}><option value="">Select programme (optional)</option>{programmes.filter(p=>p.department_id===form.department).map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></label>
                  <label>Academic level<input value={form.academic_level} onChange={(e) => setForm({...form, academic_level:e.target.value})} placeholder="e.g. 300 Level"/></label>
                  <label>Admission year<input type="number" min="1950" max="2100" value={form.admission_year} onChange={(e) => setForm({...form, admission_year:e.target.value})}/></label>
                  <label>Create password<input type="password" minLength={12} required value={form.password} onChange={(e) => setForm({...form, password:e.target.value})} placeholder="At least 12 characters"/></label>
                </div>
                <button className="primary-button full-button" disabled={busy}>{busy ? "Submitting…" : "Submit registration"} <span>→</span></button>
              </form>
            )}
            <div className="auth-switch">
              {authMode === "login" ? <>New to the portal? <button onClick={() => {setError("");setNotice("");setAuthMode("registration");}}>Start student registration</button></> :
              <>Already have an account? <button onClick={() => {setError("");setAuthMode("login");}}>Sign in</button></>}
            </div>
            <div className="security-note"><Lock size={14}/> Your information is protected by university access controls.</div>
            {!API_BASE && <div className="config-message">API connection not configured. Set <code>VITE_API_BASE_URL</code> to the Django API address to enable sign-in and registration.</div>}
          </div>
        </section>
      </main>
    );
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileNav ? "sidebar-open" : ""}`}>
        <div className="sidebar-brand"><div className="brand-mark"><Network size={21}/></div><div><b>VUNA</b><small>CISCO NETACAD</small></div><button className="mobile-close" onClick={()=>setMobileNav(false)}><X size={19}/></button></div>
        <div className="institution-label">VERITAS UNIVERSITY</div>
        {["Workspace", "Academy", "Administration"].map(group => (
          <div className="nav-group" key={group}>
            <div className="nav-group-label">{group}</div>
            {navigation.filter(item=>item.group===group).map(item => {
              const Icon=item.icon; return <button key={item.id} onClick={()=>{setView(item.id);setMobileNav(false);setError("");}} className={`nav-item ${view===item.id?"nav-active":""}`}><Icon size={18}/><span>{item.label}</span>{item.id==="students" && studentCount!==null && <small>{studentCount}</small>}</button>;
            })}
          </div>
        ))}
        <div className="sidebar-bottom"><div className="help-card"><CircleHelp size={18}/><div><b>Need help?</b><span>Contact portal support</span></div></div><button className="nav-item signout" onClick={signOut}><LogOut size={18}/><span>Sign out</span></button></div>
      </aside>
      {mobileNav && <button className="nav-scrim" aria-label="Close navigation" onClick={()=>setMobileNav(false)}/>}
      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left"><button className="mobile-menu" onClick={()=>setMobileNav(true)}><Menu/></button><div className="breadcrumbs"><span>VUNA Portal</span><b>/</b><strong>{activeNavigation?.label || "Overview"}</strong></div></div>
          <div className="topbar-actions"><div className="global-search"><Search size={16}/><input placeholder="Search the portal…" onKeyDown={(e)=>{if(e.key==="Enter"){setView("students");setSearch(e.currentTarget.value);}}}/><kbd>⌘ K</kbd></div><button className="icon-button" title="Notifications"><Bell size={18}/><i/></button><div className="user-menu"><div className="avatar">{initials(user)}</div><div className="user-meta"><b>{user.first_name} {user.last_name}</b><span>{displayRole(user.role)}</span></div><ChevronDown size={15}/></div></div>
        </header>
        <div className="page-content">
          {error && <div className="error-banner"><span>{error}</span><button onClick={()=>setError("")}><X size={16}/></button></div>}
          {notice && <div className="success-banner"><CheckCircle2 size={17}/><span>{notice}</span><button onClick={()=>setNotice("")}><X size={16}/></button></div>}
          {view==="overview" && <>
            <div className="page-heading"><div><span className="eyebrow">INSTITUTIONAL OVERVIEW</span><h1>Good day, {greeting}</h1><p>Here’s what’s happening across your student and academy workspace.</p></div><button className="outline-button" onClick={()=>loadDashboard(token||"")}><RefreshCw size={16}/> Refresh data</button></div>
            <div className="welcome-strip"><div className="welcome-icon"><GraduationCap size={25}/></div><div><b>Veritas University student management</b><span>One connected workspace for student records, professional learning and institutional operations.</span></div><div className="welcome-tag"><span/> System workspace</div></div>
            <div className="section-title"><div><h3>Registry snapshot</h3><p>Live figures retrieved from the university API</p></div><span className="live-label"><i/> API data</span></div>
            <div className="metric-grid">
              <Metric icon={<Users/>} label="Registered students" value={studentCount} note="University student records" tone="blue"/>
              <Metric icon={<Clock3/>} label="Pending verification" value={pendingCount} note="Awaiting approval" tone="amber"/>
              <Metric icon={<Building2/>} label="Faculties" value={facultyCount} note="Active academic units" tone="purple"/>
              <Metric icon={<BookOpen/>} label="Training programmes" value={null} note="Catalogue module not yet enabled" tone="green"/>
            </div>
            <div className="dashboard-grid">
              <section className="panel students-panel">
                <div className="panel-heading"><div><h3>Recently registered students</h3><p>Latest records available to your account</p></div><button className="text-button" onClick={()=>setView("students")}>View registry <span>→</span></button></div>
                <StudentTable students={students} compact/>
                {students.length===0 && <EmptyState title="No student records to display" detail="Connect the API and load verified university records to populate this table."/>}
              </section>
              <section className="panel quick-panel">
                <div className="panel-heading"><div><h3>Quick actions</h3><p>Common administrative tasks</p></div></div>
                <button className="quick-action" onClick={()=>{setView("registration");setError("");}}><div className="quick-icon blue"><UserPlus size={19}/></div><div><b>Register a student</b><span>Create an administrator-assisted record</span></div><span className="quick-arrow">→</span></button>
                <button className="quick-action" onClick={()=>setView("students")}><div className="quick-icon violet"><Users size={19}/></div><div><b>Open student registry</b><span>Search and manage student records</span></div><span className="quick-arrow">→</span></button>
                <button className="quick-action" onClick={()=>setView("faculties")}><div className="quick-icon green"><Building2 size={19}/></div><div><b>Academic structure</b><span>View faculty and department directory</span></div><span className="quick-arrow">→</span></button>
              </section>
            </div>
            <div className="footnote"><ShieldCheck size={15}/> Figures are based on API records your account is authorised to view. Unavailable values are intentionally not estimated.</div>
          </>}
          {view==="students" && <><div className="page-heading"><div><span className="eyebrow">UNIVERSITY REGISTRY</span><h1>Student registry</h1><p>Search, review and manage university student records.</p></div><button className="primary-button" onClick={()=>setView("registration")}><Plus size={17}/> Add student</button></div><div className="registry-toolbar"><div className="registry-search"><Search size={17}/><input placeholder="Search by name, matric number or email…" value={search} onChange={e=>setSearch(e.target.value)}/></div><div className="records-count">{studentCount===null?"—":studentCount.toLocaleString()} records</div></div><section className="panel registry-panel"><StudentTable students={students}/>{students.length===0&&<EmptyState title="No matching students" detail="Try another search term or create a new student record."/>}</section></>}
          {view==="registration" && <><div className="page-heading"><div><span className="eyebrow">STUDENT REGISTRY</span><h1>Register a student</h1><p>Create an administrator-assisted record. The record remains pending until verified.</p></div><button className="outline-button" onClick={()=>setView("students")}>Back to registry</button></div><section className="panel form-panel"><form onSubmit={submitAdminStudent} className="form-stack"><div className="form-grid">
            <label>Matriculation number<input required value={form.matric_number} onChange={e=>setForm({...form,matric_number:e.target.value})}/></label><label>First name<input required value={form.first_name} onChange={e=>setForm({...form,first_name:e.target.value})}/></label><label>Middle name<input value={form.middle_name} onChange={e=>setForm({...form,middle_name:e.target.value})}/></label><label>Last name<input required value={form.last_name} onChange={e=>setForm({...form,last_name:e.target.value})}/></label><label>Email address<input type="email" required value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></label><label>Phone number<input value={form.phone_number} onChange={e=>setForm({...form,phone_number:e.target.value})}/></label>
            <label>Faculty<select required value={form.faculty} onChange={e=>setForm({...form,faculty:e.target.value,department:"",programme:""})}><option value="">Select faculty</option>{faculties.map(f=><option key={f.id} value={f.id}>{f.name}</option>)}</select></label><label>Department<select required value={form.department} onChange={e=>setForm({...form,department:e.target.value,programme:""})}><option value="">Select department</option>{departments.filter(d=>d.faculty_id===form.faculty).map(d=><option key={d.id} value={d.id}>{d.name}</option>)}</select></label><label>Programme<select value={form.programme} onChange={e=>setForm({...form,programme:e.target.value})}><option value="">Select programme</option>{programmes.filter(p=>p.department_id===form.department).map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></label><label>Academic level<input value={form.academic_level} onChange={e=>setForm({...form,academic_level:e.target.value})} placeholder="e.g. 300 Level"/></label><label>Admission year<input type="number" min="1950" max="2100" value={form.admission_year} onChange={e=>setForm({...form,admission_year:e.target.value})}/></label>
          </div><div className="form-actions"><span className="muted">Registration channel: Administrator</span><button className="primary-button" disabled={busy}>{busy?"Saving…":"Create student record"} <span>→</span></button></div></form></section></>}
          {view==="faculties" && <><div className="page-heading"><div><span className="eyebrow">ACADEMIC STRUCTURE</span><h1>Faculties & departments</h1><p>Reference directory used for university student records.</p></div></div><div className="metric-grid one-metric"><Metric icon={<Building2/>} label="Faculties available" value={facultyCount} note="Visible to your account" tone="purple"/></div><section className="panel directory-panel"><div className="directory-list">{faculties.map(f=><div className="directory-item" key={f.id}><div className="quick-icon blue"><Building2 size={19}/></div><div><b>{f.name}</b><span>{f.code}</span></div><span className="directory-state">Active</span></div>)}</div>{faculties.length===0&&<EmptyState title="Academic directory unavailable" detail="Connect the API and ensure your account has permission to view the faculty directory."/ >}</section></>}
          {!["overview","students","registration","faculties"].includes(view) && <section className="module-placeholder"><div className="placeholder-icon"><Network size={27}/></div><span className="eyebrow">IMPLEMENTATION ROADMAP</span><h2>{activeNavigation?.label}</h2><p>This module is included in the approved VUNA product scope and will be delivered in a subsequent development increment. The current release focuses on identity, academic structure and the university student registry.</p><div className="placeholder-progress"><span>Current release</span><b>Registry foundation</b></div></section>}
          <footer className="page-footer"><span>VUNA Cisco NetAcad</span><span>Veritas University · Student Management Portal</span><span>Build 0.1.0</span></footer>
        </div>
      </main>
    </div>
  );
}

function Metric({icon,label,value,note,tone}:{icon:ReactNode;label:string;value:number|null;note:string;tone:string}) {
  return <div className="metric-card"><div className={`metric-icon ${tone}`}>{icon}</div><div className="metric-label">{label}</div><div className="metric-value">{value===null?"—":value.toLocaleString()}</div><div className="metric-note">{note}</div></div>;
}
function StudentTable({students,compact=false}:{students:Student[];compact?:boolean}) {
  return <div className="table-scroll"><table className="data-table"><thead><tr><th>Student</th><th>Matriculation no.</th><th>Faculty / department</th><th>Level</th><th>Status</th>{!compact&&<th>Admission year</th>}<th></th></tr></thead><tbody>{students.map(s=><tr key={s.id}><td><div className="student-cell"><div className="student-avatar">{s.first_name?.[0]}{s.last_name?.[0]}</div><div><b>{s.first_name} {s.last_name}</b><span>{s.email}</span></div></div></td><td className="mono">{s.matric_number}</td><td><div className="stacked-cell"><b>{s.faculty_name||"—"}</b><span>{s.department_name||"—"}</span></div></td><td>{s.academic_level||"—"}</td><td><span className={`status-pill ${statusClass(s.status)}`}><i/>{s.status}</span></td>{!compact&&<td>{s.admission_year||"—"}</td>}<td><button className="row-more" title="More actions"><MoreHorizontal size={18}/></button></td></tr>)}</tbody></table></div>;
}
function EmptyState({title,detail}:{title:string;detail:string}) {
  return <div className="empty-state"><div><FileText size={22}/></div><b>{title}</b><span>{detail}</span></div>;
}
