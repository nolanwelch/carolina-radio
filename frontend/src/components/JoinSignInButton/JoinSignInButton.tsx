import { Login, PlayArrow } from "@mui/icons-material";
import { Button, Link } from "@mui/material";
import NetworkService from "../../NetworkService";
import { useState, useEffect } from "react";

export default function JoinSignInButton() {
  const [isSignedIn, setIsSignedIn] = useState(false);

  useEffect(() => {
    NetworkService.isLoggedIn().then((value: boolean) => setIsSignedIn(value));
  }, [])

  return isSignedIn ?
    <Button variant="contained" startIcon={<PlayArrow />} onClick={() => {
      NetworkService.joinSession()
    }}>
      Join Radio
    </Button>
    :
    <Button component={Link} href={process.env.REACT_APP_API_URL + "/login"} variant="contained" startIcon={<Login />}>
      Sign in to Join
    </Button>
}