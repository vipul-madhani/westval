import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { styled } from '@mui/material/styles'
import MuiAppBar, { AppBarProps as MuiAppBarProps } from '@mui/material/AppBar'
import MuiDrawer from '@mui/material/Drawer'
import {
    Box,
    Toolbar,
    List,
    Typography,
    Divider,
    IconButton,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Avatar,
    Menu,
    MenuItem,
    Tooltip
} from '@mui/material'
import {
    Menu as MenuIcon,
    Dashboard as DashboardIcon,
    Assignment,
    Description,
    ListAlt,
    Warning,
    Science,
    AccountTree,
    Gavel,
    Settings,
    ChevronLeft,
    Notifications,
    Person
} from '@mui/icons-material'

const drawerWidth = 240

interface AppBarProps extends MuiAppBarProps {
    open?: boolean
}

const AppBar = styled(MuiAppBar, {
    shouldForwardProp: (prop) => prop !== 'open',
})<AppBarProps>(({ theme, open }) => ({
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(['width', 'margin'], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
    }),
    ...(open && {
        marginLeft: drawerWidth,
        width: `calc(100% - ${drawerWidth}px)`,
        transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
        }),
    }),
}))

const Drawer = styled(MuiDrawer, { shouldForwardProp: (prop) => prop !== 'open' })(
    ({ theme, open }) => ({
        '& .MuiDrawer-paper': {
            position: 'relative',
            whiteSpace: 'nowrap',
            width: drawerWidth,
            transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
            }),
            boxSizing: 'border-box',
            ...(!open && {
                overflowX: 'hidden',
                transition: theme.transitions.create('width', {
                    easing: theme.transitions.easing.sharp,
                    duration: theme.transitions.duration.leavingScreen,
                }),
                width: theme.spacing(7),
                [theme.breakpoints.up('sm')]: {
                    width: theme.spacing(9),
                },
            }),
        },
    }),
)

export default function MainLayout() {
    const navigate = useNavigate()
    const location = useLocation()
    const [open, setOpen] = useState(true)
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)

    const toggleDrawer = () => {
        setOpen(!open)
    }

    const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget)
    }

    const handleClose = () => {
        setAnchorEl(null)
    }

    const handleLogout = () => {
        localStorage.removeItem('access_token')
        navigate('/login')
    }

    const menuItems = [
        { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
        { text: 'Validation Projects', icon: <Assignment />, path: '/validation' },
        { text: 'Documents', icon: <Description />, path: '/documents' },
        { text: 'Requirements', icon: <ListAlt />, path: '/requirements' },
        { text: 'Risk Assessment', icon: <Warning />, path: '/risk' },
        { text: 'Test Management', icon: <Science />, path: '/tests' },
        { text: 'Traceability', icon: <AccountTree />, path: '/traceability' },
        { text: 'Compliance', icon: <Gavel />, path: '/compliance' },
        { text: 'Tasks', icon: <Notifications />, path: '/tasks' },
    ]

    return (
        <Box sx={{ display: 'flex' }}>
            <AppBar position="absolute" open={open}>
                <Toolbar
                    sx={{
                        pr: '24px', // keep right padding when drawer closed
                    }}
                >
                    <IconButton
                        edge="start"
                        color="inherit"
                        aria-label="open drawer"
                        onClick={toggleDrawer}
                        sx={{
                            marginRight: '36px',
                            ...(open && { display: 'none' }),
                        }}
                    >
                        <MenuIcon />
                    </IconButton>
                    <Typography
                        component="h1"
                        variant="h6"
                        color="inherit"
                        noWrap
                        sx={{ flexGrow: 1 }}
                    >
                        Westval Validation Lifecycle Management
                    </Typography>
                    <IconButton color="inherit">
                        <Notifications />
                    </IconButton>
                    <Box sx={{ ml: 2 }}>
                        <Tooltip title="Account settings">
                            <IconButton
                                onClick={handleMenu}
                                size="small"
                                sx={{ ml: 2 }}
                                aria-controls={Boolean(anchorEl) ? 'account-menu' : undefined}
                                aria-haspopup="true"
                                aria-expanded={Boolean(anchorEl) ? 'true' : undefined}
                            >
                                <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                                    <Person />
                                </Avatar>
                            </IconButton>
                        </Tooltip>
                        <Menu
                            anchorEl={anchorEl}
                            id="account-menu"
                            open={Boolean(anchorEl)}
                            onClose={handleClose}
                            onClick={handleClose}
                            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                        >
                            <MenuItem onClick={handleClose}>Profile</MenuItem>
                            <MenuItem onClick={handleClose}>My Account</MenuItem>
                            <Divider />
                            <MenuItem onClick={handleLogout}>Logout</MenuItem>
                        </Menu>
                    </Box>
                </Toolbar>
            </AppBar>
            <Drawer variant="permanent" open={open}>
                <Toolbar
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'flex-end',
                        px: [1],
                    }}
                >
                    <IconButton onClick={toggleDrawer}>
                        <ChevronLeft />
                    </IconButton>
                </Toolbar>
                <Divider />
                <List component="nav">
                    {menuItems.map((item) => (
                        <ListItemButton
                            key={item.text}
                            onClick={() => navigate(item.path)}
                            selected={location.pathname === item.path}
                        >
                            <ListItemIcon>
                                {item.icon}
                            </ListItemIcon>
                            <ListItemText primary={item.text} />
                        </ListItemButton>
                    ))}
                    <Divider sx={{ my: 1 }} />
                    <ListItemButton onClick={() => navigate('/settings')}>
                        <ListItemIcon>
                            <Settings />
                        </ListItemIcon>
                        <ListItemText primary="Settings" />
                    </ListItemButton>
                </List>
            </Drawer>
            <Box
                component="main"
                sx={{
                    backgroundColor: (theme) =>
                        theme.palette.mode === 'light'
                            ? theme.palette.grey[100]
                            : theme.palette.grey[900],
                    flexGrow: 1,
                    height: '100vh',
                    overflow: 'auto',
                }}
            >
                <Toolbar />
                <Box sx={{ p: 3 }}>
                    <Outlet />
                </Box>
            </Box>
        </Box>
    )
}
