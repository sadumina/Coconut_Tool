import { Link, useLocation } from "react-router-dom";
import { Drawer, List, ListItemButton, ListItemText } from "@mui/material";

const menu = [
  { label: "Dashboard", path: "/" },
  { label: "Production", path: "/production" },
  { label: "Analytics", path: "/analytics" },
  { label: "Settings", path: "/settings" },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <Drawer variant="permanent" anchor="left"
      sx={{ width: 220, [`& .MuiDrawer-paper`]: { width: 220 } }}>
      <h2 style={{ padding: "20px" }}>🥥 Coconut UI</h2>
      <List>
        {menu.map((item, idx) => (
          <ListItemButton
            key={idx}
            component={Link}
            to={item.path}
            selected={location.pathname === item.path}
          >
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Drawer>
  );
}
