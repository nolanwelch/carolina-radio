import { Login, PlayArrow } from "@mui/icons-material";
import { Button } from "@mui/material";
import Cookies from "js-cookie";

export default function JoinSignInButton() {
  const isSignedIn: boolean = Cookies.get("accessToken") ? true : false;

  return isSignedIn ?
    <Button variant="contained" startIcon={<PlayArrow />}>
      Join Radio
    </Button>
    :
    <Button variant="contained" startIcon={<Login />}>
      Sign in to Join
    </Button >
}