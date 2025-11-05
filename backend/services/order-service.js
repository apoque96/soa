import express from "express";
import cors from "cors";
import { v4 as uuid } from "uuid";

const app = express();
app.use(cors());
app.use(express.json());

const purchases = [];
const makeCode = ()=> "BETA-" + uuid().slice(0,8).toUpperCase();

app.post("/purchase", (req,res)=>{
  const { userId, planId, priceSnapshot } = req.body || {};
  if(!userId || !planId) return res.status(400).json({ ok:false, msg:"userId y planId requeridos" });
  const code = makeCode();
  const p = { id:uuid(), userId, planId, code, priceSnapshot: priceSnapshot ?? null, purchasedAt:new Date().toISOString() };
  purchases.push(p); res.json({ ok:true, purchase:p });
});

app.get("/purchases", (req,res)=>{
  const userId = req.query.userId || "";
  res.json({ ok:true, purchases: purchases.filter(p=>p.userId===userId) });
});

app.post("/validate", (req,res)=>{
  const { code } = req.body || {};
  const found = purchases.find(p=>p.code===code);
  if(!found) return res.status(404).json({ ok:false, msg:"Código no encontrado" });
  res.json({ ok:true, license:found });
});

app.get("/health", (_req,res)=> res.json({ ok:true, service:"order/licensing (Empresa B)", port:3003, purchases:purchases.length }));

const PORT = 3003;
app.listen(PORT, ()=> console.log(`Order/Licensing (Empresa B) en http://localhost:${PORT}`));
