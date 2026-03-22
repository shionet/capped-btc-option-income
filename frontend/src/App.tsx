import { Layout, Menu, theme } from "antd";
import { BrowserRouter, Link, useLocation } from "react-router-dom";
import AppRoutes from "./router";

const { Header, Content } = Layout;

function InnerApp() {
  const { token } = theme.useToken();
  const location = useLocation();
  const selectedKey = location.pathname === "/" ? "/" : `/${location.pathname.split("/")[1]}`;

  return (
    <Layout style={{ minHeight: "100vh", background: token.colorBgLayout }}>
      <Header style={{ display: "flex", alignItems: "center" }}>
        <div style={{ color: "white", fontWeight: 700, marginRight: 24 }}>Crypto Option Income</div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[selectedKey]}
          items={[
            { key: "/", label: <Link to="/">Dashboard</Link> },
            { key: "/recommendations", label: <Link to="/recommendations">推荐策略</Link> },
            { key: "/risk-check", label: <Link to="/risk-check">风控检查</Link> },
            { key: "/execution-preview", label: <Link to="/execution-preview">执行预演</Link> }
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
