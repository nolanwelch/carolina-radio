import { PlayArrow } from "@mui/icons-material";
import { Button } from "@mui/material";

export default function JoinSignInButton() {
  return (
    <Button variant="contained" startIcon={<PlayArrow />}>
      Sign in to Join
    </Button>
  );
}