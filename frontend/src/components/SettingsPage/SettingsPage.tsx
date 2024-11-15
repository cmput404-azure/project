import TableCell, { tableCellClasses } from '@mui/material/TableCell';

import Paper from '@mui/material/Paper';
import { Switch } from "@mui/material";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import { styled } from '@mui/material/styles';
import styles from './SettingsPage.module.scss';
import setting from '../../service/setting';
import { useEffect, useState } from 'react';

const StyledTableCell = styled(TableCell)(() => ({
   [`&.${tableCellClasses.head}`]: {
      backgroundColor: '#333',
      color: '#fff',
      fontWeight: 'bold',
      borderBottom: `2px solid #444`,
   },
   [`&.${tableCellClasses.body}`]: {
      fontSize: 14,
      backgroundColor: '#222',
      color: '#ddd',
      borderBottom: `1px solid #444`,
      padding: '10px 15px',
   },
}));

const StyledTableRow = styled(TableRow)(() => ({
   '&:last-child td, &:last-child th': {
      border: 0,
   },
}));

export default function CustomizedTables() {
   const [requireApproval, setRequireApproval] = useState(true);
   const [rows, setRows] = useState([]);

   function createData (host: string, username: string, password: string, status: boolean) {
      return { host, username, password, status };
   }

   const handleToggle = async () => {
      const newStatus = !requireApproval;
      await setting.updateToggle(newStatus);
      setRequireApproval(newStatus);
   }

   useEffect(() => {
      const fetchConfig = async () => {
         const val = await setting.getToggleValue();
         setRequireApproval(val);
      };

      const fetchNodeList = async () => {
         const fetchedData = await setting.getNodeList();
   
         const nodeRows = fetchedData.map((node: any) => {
            return createData(node.host, node.username, node.password, node.is_authenticated);
         });

         setRows(nodeRows);
      }

      fetchConfig();
      fetchNodeList();
   }, []);

   return (
      <div className={styles.settings}>
         <h1 className={styles.title}>Admin Settings</h1>
         <div className={styles.registration__toggle}>
            <p>Toggle registration approval</p>
            <Switch checked={requireApproval} onChange={handleToggle}/>
         </div>
         <TableContainer component={Paper}>
            <Table sx={{ minWidth: 700 }} aria-label="customized table">
               <TableHead>
                  <TableRow>
                     <StyledTableCell>Node URL</StyledTableCell>
                     <StyledTableCell>Username</StyledTableCell>
                     <StyledTableCell>Password</StyledTableCell>
                     <StyledTableCell>Status</StyledTableCell>
                     {/* <StyledTableCell>Actions</StyledTableCell> */}
                  </TableRow>
               </TableHead>
               <TableBody>
                  {rows.map((row) => (
                     <StyledTableRow key={row.host}>
                        <StyledTableCell component="th" scope="row">
                           {row.host}
                        </StyledTableCell>
                        <StyledTableCell>{row.username}</StyledTableCell>
                        <StyledTableCell>{row.password}</StyledTableCell>
                        <StyledTableCell
                           style={{
                              fontWeight: 'bold',
                              color: row.status ? 'green' : 'red',
                              backgroundColor: row.status ? '#e0ffe0' : '#ffe0e0',
                              padding: '10px 15px',
                              fontSize: '14px'
                           }}
                        >
                           {row.status ? 'CONNECTED' : 'NOT CONNECTED'}
                        </StyledTableCell>
                     </StyledTableRow>
                  ))}
               </TableBody>
            </Table>
         </TableContainer>
      </div>
   );
}