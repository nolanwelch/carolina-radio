import { Box, Tab, Tabs } from '@mui/material';
import { useState } from 'react';
import MyQueue from './MyQueue/MyQueue';
import Song from '../types/Song';
import NextUp from './NextUp/NextUp';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      style={{ overflowY: "scroll", height: "calc(100% - 48.8px)" }}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function AppTabs(props: {queuedSongs: Song[]}) {
  const [value, setValue] = useState(0);
  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs variant="fullWidth" value={value} onChange={handleChange} aria-label="basic tabs example">
          <Tab label="Next Up" />
          <Tab label="My Queue" />
        </Tabs>
      </Box>
      <TabPanel value={value} index={0}>
        <NextUp songs={props.queuedSongs} />
      </TabPanel>
      <TabPanel value={value} index={1}>
        <MyQueue />
      </TabPanel>
    </>
  );
}

export default AppTabs;