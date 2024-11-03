import Cookies from "js-cookie";
import QueueSong from "../QueueSong/QueueSong";
import styles from "./MyQueue.module.css";
import { Button, Link, Typography } from "@mui/material";
import { Login } from "@mui/icons-material";

export default function MyQueue() {
    // TODO: Update this to instead request an endpoint to confirm they're logged in
    const isSignedIn: boolean = Cookies.get("accessToken") ? true : false;
    
    if (isSignedIn) {
        return (
            <QueueSong />
        )
    } else {
        return (
            <div className={styles.loggedOutDisplay}>
                <Typography variant="h6">You must be logged in to add to the queue</Typography>
                <Button component={Link} href={process.env.REACT_APP_API_URL + "/login"} variant="contained" startIcon={<Login />}>
                    Sign in
                </Button>
            </div>
        )
    }
}