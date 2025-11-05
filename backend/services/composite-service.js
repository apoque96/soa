import express from "express";
import cors from "cors";
import { send } from "../esb/bus.js";
import { validateContract } from "../esb/contracts.js";

const app = express();
app.use(cors());
app.use(express.json());

app.post("/soac/register", async (req, res) => {
    const v = validateContract("REGISTER", req.body || {}); if(!v.ok) return res.status(400).json(v);
    const r = await send({ service:"AUTH", action:"REGISTER", payload:req.body });
    res.status(r.status).json(r.data);
});
app.post("/soac/login", async (req, res) => {
    const v = validateContract("LOGIN", req.body || {}); if(!v.ok) return res.status(400).json(v);
    const r = await send({ service:"AUTH", action:"LOGIN", payload:req.body });
    res.status(r.status).json(r.data);
});

app.get("/soac/plans", async (_req, res) => {
    const r = await send({ service:"CATALOG", action:"LIST_PLANS" });
    res.status(r.status).json(r.data);
});
app.post("/soac/plans", async (req, res) => {
    const v = validateContract("CREATE_PLAN", req.body || {}); if(!v.ok) return res.status(400).json(v);
    const isAdmin = (req.headers["x-admin"]||"").toString()==="true";
    const r = await send({ service:"CATALOG", action:"CREATE_PLAN", payload:req.body, headers: { "x-admin": isAdmin ? "true":"false" } });
    res.status(r.status).json(r.data);
});

app.post("/soac/purchase", async (req, res) => {
    const v = validateContract("PURCHASE", req.body || {}); if(!v.ok) return res.status(400).json(v);

    const plans = await send({ service:"CATALOG", action:"LIST_PLANS" });
    const list = plans.data?.plans || [];
    if (!list.find(p => p.id === req.body.planId)) {
        return res.status(404).json({ ok:false, msg:"El plan no existe (verificado con Empresa A)" });
    }

    const r = await send({ service:"ORDER", action:"PURCHASE", payload:req.body });
    res.status(r.status).json(r.data);
});

app.get("/soac/my-purchases", async (req, res) => {
    const userId = req.query.userId || "";
    const v = validateContract("LIST_PURCHASES", { userId }); if(!v.ok) return res.status(400).json(v);
    const r = await send({ service:"ORDER", action:"LIST_PURCHASES", payload:{ userId } });
    res.status(r.status).json(r.data);
});
app.post("/soac/validate", async (req, res) => {
    const v = validateContract("VALIDATE", req.body || {}); if(!v.ok) return res.status(400).json(v);
    const r = await send({ service:"ORDER", action:"VALIDATE", payload:req.body });
    res.status(r.status).json(r.data);
});

app.get("/health", (_req,res)=> res.json({ ok:true, service:"orchestrator", port:3004 }));

const PORT = 3004;
app.listen(PORT, ()=> console.log(`Composite/Orchestrator en http://localhost:${PORT}`));
