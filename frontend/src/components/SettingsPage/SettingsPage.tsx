import { Box, Button, Checkbox, FormControl, FormControlLabel, IconButton, InputLabel, MenuItem, Modal, Select, Switch, TextField, Tooltip } from "@mui/material";
import TableCell, { tableCellClasses } from '@mui/material/TableCell';
import { useEffect, useState } from 'react';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import DeleteIcon from '@mui/icons-material/Delete';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import setting from '../../service/setting';
import { styled } from '@mui/material/styles';
import styles from './SettingsPage.module.scss';

const StyledTextField = styled(TextField)(() => ({
   '& .MuiInputBase-root': {
      color: 'white',
   },
   '& .MuiInputLabel-root': {
      color: 'white',
   },
   '& .MuiOutlinedInput-root': {
      '& fieldset': {
         borderColor: 'transparent',
         borderWidth: '1px',
      },
      '&:hover fieldset': {
         borderColor: 'white',
      },
      '&.Mui-focused fieldset': {
         borderColor: '#70ffaf',
      },
      backgroundColor: '#2b2b2b',
      borderRadius: '5px',
      transition: 'border-color 0.3s ease',
   },
   '& .MuiInputLabel-root.Mui-focused': {
      color: 'white',
   },
   alignSelf: 'center',
}));

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
   const [modalOpen, setModalOpen] = useState(false);
   const [editingNode, setEditingNode] = useState(null);
   const [protocol, setProtocol] = useState('http://');
   const [nodeUrl, setNodeUrl] = useState('');
   const [username, setUsername] = useState('');
   const [password, setPassword] = useState('');
   const [status, setStatus] = useState(true);
   const [errorMessage, setErrorMessage] = useState('');
   const [oldHost, setOldHost] = useState('');

   function createData(host: string, username: string, password: string, status: boolean) {
      return { host, username, password, status };
   }

   const handleToggle = async () => {
      const newStatus = !requireApproval;
      await setting.updateToggle(newStatus);
      setRequireApproval(newStatus);
   }

   const handleOpenModal = (node = null) => {
      setErrorMessage('');
      if (node) { // editing existing node
         if (node.host) setOldHost(node.host); // Need old value to get entry in DB
         setEditingNode(node);

         const { protocol, hostname, port } = new URL(node.host);
         const normalizedProtocol = protocol.includes('https') ? 'https://' : 'http://';
         setNodeUrl(`${hostname}${port ? `:${port}` : ''}`);
         setProtocol(normalizedProtocol);
         setUsername(node.username);
         setPassword(node.password);
         setStatus(node.status);
      } else {
         setEditingNode(null);
         setProtocol('http://');
         setNodeUrl('');
         setUsername('');
         setPassword('');
      }
      setModalOpen(true);
   }

   const handleCloseModal = () => {
      setModalOpen(false);
      setOldHost('');
   }

   const handleSave = async () => {
      setErrorMessage('');
      const fullUrl = `${protocol}${nodeUrl}`;

      try {
         let response;
         if (editingNode) {
            response = await setting.updateNode(username, password, fullUrl, status, oldHost);
         } else {
            response = await setting.addNode(username, password, fullUrl);
         }

         if (response.error) {
            setErrorMessage(response.error);
         } else {
            setErrorMessage('');
            fetchNodeList();
            handleCloseModal();
         }
      } catch (error) {
         console.error('Error processing node:', error);
         setErrorMessage('Something went wrong. Please try again later.');
      }
   }
   const handleDelete = async (username) => {
      try {
         const response = await setting.deleteNode(username);
         fetchNodeList();

      } catch (error) {
         console.error('Error deleting node:', error);
      }
   };

   const fetchNodeList = async () => {
      const fetchedData = await setting.getNodeList();

      const nodeRows = fetchedData.map((node: any) => {
         return createData(node.host, node.username, node.password, node.is_authenticated);
      });

      setRows(nodeRows);
   }

   useEffect(() => {
      const fetchConfig = async () => {
         const val = await setting.getToggleValue();
         setRequireApproval(val);
      };

      fetchConfig();
      fetchNodeList();
   }, []);

   return (
      <div className={styles.settings}>
         <h1 className={styles.title}>Admin Settings</h1>
         <div className={styles.registration__toggle}>
            <p>Toggle registration approval</p>
            <Switch checked={requireApproval} onChange={handleToggle} />
         </div>
         <Button
            variant="contained"
            color="primary"
            onClick={() => handleOpenModal()}
            sx={{
               width: '15%',
               backgroundColor: '#70ffaf',
               color: '#1a1a1a',
               fontWeight: 'bold',
               fontSize: '12px',
               padding: '0.5rem',
               border: 'none',
               borderRadius: '8px',
               cursor: 'pointer',
               transition: 'background-color 0.3s',
               '&:hover': {
                  backgroundColor: '#30fb88',
               },
               marginBottom: '1rem',
               alignSelf: 'flex-end',
            }}
         >
            New Connection
         </Button>
         <TableContainer component={Paper}>
            <Table sx={{ minWidth: 700 }} aria-label="customized table">
               <TableHead>
                  <TableRow>
                     <StyledTableCell>
                        <Box display="flex" alignItems="center">
                           Node URL
                           <Tooltip title="Double-click entry to edit" arrow>
                              <HelpOutlineIcon
                                 sx={{
                                    fontSize: 16,
                                    marginLeft: '5px',
                                    color: 'grey',
                                    cursor: 'pointer',
                                 }}
                              />
                           </Tooltip>
                        </Box>
                     </StyledTableCell>
                     <StyledTableCell>Username</StyledTableCell>
                     <StyledTableCell>Password</StyledTableCell>
                     <StyledTableCell>Incoming Requests</StyledTableCell>
                  </TableRow>
               </TableHead>
               <TableBody>
                  {rows.map((row) => (
                     <StyledTableRow key={row.host}
                        onDoubleClick={() => handleOpenModal(row)}
                     >
                        <StyledTableCell component="th" scope="row">
                           {row.host}
                           <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleDelete(row.username)}
                           >
                              <DeleteIcon />
                           </IconButton>
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
                           {row.status ? 'ALLOWED' : 'NOT ALLOWED'}
                        </StyledTableCell>
                     </StyledTableRow>
                  ))}
               </TableBody>
            </Table>
         </TableContainer>

         {/* Modal for adding/editing nodes */}
         <Modal
            open={modalOpen}
            onClose={handleCloseModal}
            aria-labelledby="modal-title"
            aria-describedby="modal-description"
         >
            <Box
               sx={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  backgroundColor: '#1a1a1a',
                  padding: '20px',
                  borderRadius: '8px',
                  boxShadow: 24,
                  width: '400px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: 'none',
                  outline: 'none',
                  '&:focus': {
                     outline: 'none',
                  },
               }}
            >
               <h3 id="modal-title">
                  {editingNode ? 'Update Node' : 'Add Node'}
               </h3>
               <form onSubmit={handleSave}>
                  <Box display="flex" alignItems="center" gap={1} marginBottom={2} width="100%">
                     <FormControl size="small" variant="outlined"
                        sx={{
                           minWidth: 'fit-content',
                           '& .MuiOutlinedInput-root': {
                              '&:hover fieldset': {
                                 borderColor: 'white',
                              },
                              '&.Mui-focused fieldset': {
                                 borderColor: 'transparent',
                                 borderWidth: 1,
                              },
                           },
                           '& .MuiInputLabel-root': {
                              color: 'white',
                              '&.Mui-focused': {
                                 color: 'white',
                              },
                           },
                           '& .MuiSelect-icon': {
                              color: 'white',
                           },
                        }}
                     >
                        <InputLabel id="protocol-select-label" sx={{ color: 'white' }}>Protocol</InputLabel>
                        <Select
                           labelId="protocol-select-label"
                           id="protocol-select"
                           value={protocol}
                           onChange={(e) => setProtocol(e.target.value)}
                           label="Protocol"
                           sx={{
                              backgroundColor: '#333',
                              color: 'white',
                           }}
                        >
                           <MenuItem value="http://">http://</MenuItem>
                           <MenuItem value="https://">https://</MenuItem>
                        </Select>
                     </FormControl>

                     <StyledTextField
                        label="Host"
                        variant="outlined"
                        size="small"
                        value={nodeUrl}
                        onChange={(e) => setNodeUrl(e.target.value)}
                        required
                        fullWidth
                        sx={{ flexGrow: 1 }}
                     />
                  </Box>
                  <StyledTextField
                     label="Node name"
                     variant="outlined"
                     size="small"
                     value={username}
                     onChange={(e) => setUsername(e.target.value)}
                     required
                     fullWidth
                     sx={{
                        marginBottom: '1rem',
                     }}
                  />
                  <StyledTextField
                     label="Password"
                     variant="outlined"
                     size="small"
                     value={password}
                     onChange={(e) => setPassword(e.target.value)}
                     required
                     fullWidth
                     type="password"
                     sx={{
                        marginBottom: '1rem',
                     }}
                  />
                  {editingNode && (
                     <FormControlLabel
                        control={
                           <Checkbox
                              checked={status}
                              onChange={(e) => setStatus(e.target.checked)}
                              sx={{
                                 color: 'white',
                                 '&.Mui-checked': {
                                    color: '#70ffaf',
                                 },
                              }}
                           />
                        }
                        label="Allow Connection"
                        sx={{
                           color: 'white',
                           marginBottom: '1rem',
                        }}
                     />
                  )}

                  {errorMessage && <p className={styles.error__message}>{errorMessage}</p>}
                  <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                     <Button
                        type="submit"
                        variant="contained"
                        color="primary"
                        fullWidth
                        sx={{
                           width: '20%',
                           backgroundColor: '#70ffaf',
                           color: '#1a1a1a',
                           fontWeight: 'bold',
                           fontSize: '12px',
                           padding: '0.8rem',
                           border: 'none',
                           borderRadius: '8px',
                           cursor: 'pointer',
                           transition: 'background-color 0.3s',
                           '&:hover': {
                              backgroundColor: '#30fb88',
                           },
                        }}
                        disabled={!nodeUrl || !username || !password}
                     >
                        Save
                     </Button>
                  </div>
               </form>
            </Box>
         </Modal>
      </div>
   );
}