import { Login, PlayArrow } from "@mui/icons-material";
import { Button, Link } from "@mui/material";
import NetworkService from "../../NetworkService";

export default function JoinSignInButton() {
  const isSignedIn: boolean = NetworkService.isLoggedIn();

  return isSignedIn ?
    <Button variant="contained" startIcon={<PlayArrow />}>
      Join Radio
    </Button>
    :
    <Button component={Link} href={process.env.REACT_APP_API_URL + "/login"} variant="contained" startIcon={<Login />}>
      Sign in to Join
    </Button>
}