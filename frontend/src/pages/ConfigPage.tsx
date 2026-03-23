import { Button, Card, Input, Select, Space, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { fetchConfig, updateConfig } from "../api/config";
import { fetchTradingMode, updateTradingMode } from "../api/trading";
import { TradingMode } from "../types/domain";

export default function ConfigPage() {
  const [domain, setDomain] = useState<"strategy" | "risk" | "execution">("strategy");
  const [content, setContent] = useState("{}");
  const [mode, setMode] = useState<TradingMode>("DRY_RUN");

  const loadConfig = (nextDomain: "strategy" | "risk" | "execution") => {
    fetchConfig(nextDomain).then((res) => {
      setContent(JSON.stringify(res.data.payload ?? {}, null, 2));
    });
  };

  useEffect(() => {
    loadConfig(domain);
    fetchTradingMode().then((res) => setMode(res.data.mode));
  }, [domain]);

  const onSave = async () => {
    try {
      const payload = JSON.parse(content);
      await updateConfig(domain, payload, true);
      message.success("Configuration saved");
    } catch (err) {
      message.error(`Invalid JSON or save failed: ${String(err)}`);
    }
  };

  const onModeSave = async () => {
    try {
      await updateTradingMode(mode);
      message.success("Trading mode updated");
    } catch (err) {
      message.error(String(err));
    }
  };

  return (
    <>
      <Typography.Title level={3}>Config Center</Typography.Title>
      <Card title="Trading Mode" style={{ marginBottom: 16 }}>
        <Space>
          <Select<TradingMode>
            value={mode}
            style={{ width: 220 }}
            onChange={(v) => setMode(v)}
            options={[
              { value: "DRY_RUN", label: "DRY_RUN" },
              { value: "SEMI_AUTO", label: "SEMI_AUTO" },
              { value: "LIVE_TRADING", label: "LIVE_TRADING" }
            ]}
          />
          <Button type="primary" onClick={onModeSave}>Update Mode</Button>
        </Space>
      </Card>
      <Card title="Strategy/Risk/Execution Params">
        <Space direction="vertical" style={{ width: "100%" }}>
          <Select
            value={domain}
            style={{ width: 220 }}
            onChange={(v) => setDomain(v)}
            options={[
              { value: "strategy", label: "Strategy" },
              { value: "risk", label: "Risk" },
              { value: "execution", label: "Execution" }
            ]}
          />
          <Input.TextArea value={content} onChange={(e) => setContent(e.target.value)} autoSize={{ minRows: 16 }} />
          <Space>
            <Button onClick={() => loadConfig(domain)}>Reload</Button>
            <Button type="primary" onClick={onSave}>Save & Publish</Button>
          </Space>
        </Space>
      </Card>
    </>
  );
}
