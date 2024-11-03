import QueueSong from "../QueueSong/QueueSong";
import styles from "./MyQueue.module.css";
import { Button, Link, Typography } from "@mui/material";
import { Login } from "@mui/icons-material";
import NetworkService from "../../NetworkService";

export default function MyQueue() {
  const isSignedIn: boolean = NetworkService.isLoggedIn();

  return isSignedIn ?
    <QueueSong />
    :
    <div className={styles.loggedOutDisplay}>
      <Typography variant="h6">You must be logged in to add to the queue</Typography>
      <Button component={Link} href={process.env.REACT_APP_API_URL + "/login"} variant="contained" startIcon={<Login />}>
        Sign in
      </Button>
    </div>
}