import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";

const app = express();
app.use(cors());
app.use(express.json());

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const FRONT_DIR = path.resolve(__dirname, "../front");

const ORCH_URL   = "http://localhost:3004";
const AUTH_URL   = "http://localhost:3001";
const CATALOG_URL= "http://localhost:3002";
const ORDER_URL  = "http://localhost:3003";

async function forward(method, base, route, body=null, headers={}){
  try{
    const res = await fetch(`${base}${route}`, { method, headers:{ "Content-Type":"application/json", ...headers }, body: body?JSON.stringify(body):undefined });
    const text=await res.text(); let data; try{ data=text?JSON.parse(text):{}; }catch{ data={ ok:false, raw:text }; }
    return { status:res.status, data };
  }catch(e){ return { status:502, data:{ ok:false, msg:`No se pudo contactar a ${base}${route}`, error:String(e) } }; }
}

app.post("/api/register", async (req,res)=> res.status((await forward("POST", ORCH_URL, "/soac/register", req.body)).status).json((await forward("POST", ORCH_URL, "/soac/register", req.body)).data));
app.post("/api/login",    async (req,res)=> res.status((await forward("POST", ORCH_URL, "/soac/login", req.body)).status   ).json((await forward("POST", ORCH_URL, "/soac/login", req.body)).data));

app.get ("/api/plans",    async (_req,res)=> res.status((await forward("GET",  ORCH_URL, "/soac/plans")).status            ).json((await forward("GET",  ORCH_URL, "/soac/plans")).data));
app.post("/api/plans",    async (req,res)=> res.status((await forward("POST", ORCH_URL, "/soac/plans", req.body, { "x-admin": req.headers["x-admin"]||"false" })).status).json((await forward("POST", ORCH_URL, "/soac/plans", req.body, { "x-admin": req.headers["x-admin"]||"false" })).data));

app.post("/api/purchase", async (req,res)=> res.status((await forward("POST", ORCH_URL, "/soac/purchase", req.body)).status).json((await forward("POST", ORCH_URL, "/soac/purchase", req.body)).data));
app.get ("/api/my-purchases", async (req,res)=> {
  const qs = req.url.split("?")[1] ? "?" + req.url.split("?")[1] : "";
  const { status, data } = await forward("GET", ORCH_URL, "/soac/my-purchases"+qs);
  res.status(status).json(data);
});
app.post("/api/validate", async (req,res)=> res.status((await forward("POST", ORCH_URL, "/soac/validate", req.body)).status).json((await forward("POST", ORCH_URL, "/soac/validate", req.body)).data));

app.get("/api/health", async (_req,res)=>{
  const [orch, a, b, c] = await Promise.all([
    forward("GET", ORCH_URL, "/health"),
    forward("GET", AUTH_URL, "/health"),
    forward("GET", CATALOG_URL, "/health"),
    forward("GET", ORDER_URL, "/health"),
  ]);
  res.json({ gateway:{ ok:true, port:3000 }, orchestrator: orch.data, auth:a.data, catalog:b.data, order:c.data });
});

app.get("/api/topology", (_req,res)=>{
  res.json({
    gateway: { name:"API Gateway", baseUrl:"http://localhost:3000" },
    orchestrator: { name:"Composite Orchestrator", baseUrl: ORCH_URL },
    bus: { name:"Enterprise Service Bus", kind:"Registry + Canonical Message Router" },
    companies: [
      { name:"Empresa A (Proveedor de Catálogo)", tag:"Oferta/Productos", services:[ { name:"Catalog Service", baseUrl: CATALOG_URL } ] },
      { name:"Empresa B (Licenciamiento)", tag:"Ventas/Accesos", services:[ { name:"Order/Licensing Service", baseUrl: ORDER_URL } ] },
      { name:"Identidad", tag:"Transversal", services:[ { name:"Auth Service", baseUrl: AUTH_URL } ] }
    ]
  });
});

app.use("/", express.static(FRONT_DIR));

const PORT = 3000;
app.listen(PORT, ()=>{ console.log(`Gateway http://localhost:${PORT}`); console.log(`Front -> ${FRONT_DIR}`); });
