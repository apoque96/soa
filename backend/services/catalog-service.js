import express from "express";
import cors from "cors";
import { v4 as uuid } from "uuid";

const app = express();
app.use(cors());
app.use(express.json());

const plans = [
  { id:"p-basic", name:"Basic", price:9.99, description:"Plan básico para empezar", createdBy:"u-admin", createdAt:new Date().toISOString() }
];

app.get("/plans", (_req,res)=> res.json({ ok:true, plans }));

app.post("/plans", (req,res)=>{
  const isAdmin = (req.headers["x-admin"]||"").toString()==="true";
  if(!isAdmin) return res.status(403).json({ ok:false, msg:"Solo admin puede crear planes (demo)" });
  const { name, price, description, createdBy } = req.body || {};
  if(!name || price==null) return res.status(400).json({ ok:false, msg:"name y price requeridos" });
  const plan = { id:uuid(), name, price:Number(price), description:description||"", createdBy:createdBy||"u-admin", createdAt:new Date().toISOString() };
  plans.push(plan); res.json({ ok:true, plan });
});

app.get("/health", (_req,res)=> res.json({ ok:true, service:"catalog (Empresa A)", port:3002, plans:plans.length }));

const PORT = 3002;
app.listen(PORT, ()=> console.log(`Catalog (Empresa A) en http://localhost:${PORT}`));
