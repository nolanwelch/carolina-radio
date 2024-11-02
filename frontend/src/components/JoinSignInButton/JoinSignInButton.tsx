import { Login, PlayArrow } from "@mui/icons-material";
import { Button, Link } from "@mui/material";
import Cookies from "js-cookie";

export default function JoinSignInButton() {
  const isSignedIn: boolean = Cookies.get("accessToken") ? true : false;

  return isSignedIn ?
    <Button variant="contained" startIcon={<PlayArrow />}>
      Join Radio
    </Button>
    :
    <Button component={Link} href="https://api.carolinaradio.tech/login" variant="contained" startIcon={<Login />}>
      Sign in to Join
    </Button>
}