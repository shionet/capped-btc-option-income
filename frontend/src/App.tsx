import { Layout, Menu, theme } from "antd";
import { BrowserRouter, Link, useLocation } from "react-router-dom";
import AppRoutes from "./router";

const { Header, Content } = Layout;

function InnerApp() {
  const { token } = theme.useToken();
  const location = useLocation();
  const selectedKey = location.pathname === "/" ? "/dashboard" : `/${location.pathname.split("/")[1]}`;

  return (
    <Layout style={{ minHeight: "100vh", background: token.colorBgLayout }}>
      <Header style={{ display: "flex", alignItems: "center" }}>
        <div style={{ color: "white", fontWeight: 700, marginRight: 24 }}>Crypto Option Income</div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[selectedKey]}
          items={[
            { key: "/dashboard", label: <Link to="/dashboard">Dashboard</Link> },
            { key: "/strategies", label: <Link to="/strategies">Strategies</Link> },
            { key: "/positions", label: <Link to="/positions">Positions</Link> },
            { key: "/pnl", label: <Link to="/pnl">PnL</Link> },
            { key: "/risk", label: <Link to="/risk">Risk</Link> },
            { key: "/config", label: <Link to="/config">Config</Link> },
            { key: "/execution-monitor", label: <Link to="/execution-monitor">Execution</Link> },
          ]}
        />
      </Header>
      <Content style={{ padding: 24, maxWidth: 1400, margin: "0 auto", width: "100%" }}>
        <AppRoutes />
      </Content>
    </Layout>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <InnerApp />
    </BrowserRouter>
  );
}
