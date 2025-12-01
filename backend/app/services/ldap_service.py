"""LDAP/Active Directory authentication service"""
import ldap3
from ldap3 import Server, Connection, ALL, NTLM
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class LDAPService:
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate user against LDAP/AD"""
        if not current_app.config['LDAP_ENABLED']:
            return None
        
        try:
            if current_app.config['AUTH_TYPE'] == 'ad':
                return LDAPService._authenticate_ad(username, password)
            else:
                return LDAPService._authenticate_ldap(username, password)
        except Exception as e:
            logger.error(f'LDAP authentication failed: {str(e)}')
            return None
    
    @staticmethod
    def _authenticate_ldap(username, password):
        """Authenticate against standard LDAP"""
        host = current_app.config['LDAP_HOST']
        port = current_app.config['LDAP_PORT']
        use_ssl = current_app.config['LDAP_USE_SSL']
        base_dn = current_app.config['LDAP_BASE_DN']
        user_dn_template = current_app.config['LDAP_USER_DN']
        username_attr = current_app.config['LDAP_USERNAME_ATTRIBUTE']
        
        # Create server
        server = Server(host, port=port, use_ssl=use_ssl, get_info=ALL)
        
        # Build user DN
        if '{username}' in user_dn_template:
            user_dn = user_dn_template.format(username=username)
        else:
            user_dn = f'{username_attr}={username},{user_dn_template}'
        
        # Attempt bind
        conn = Connection(server, user=user_dn, password=password, auto_bind=True)
        
        if not conn.bound:
            return None
        
        # Search for user details
        search_filter = f'({username_attr}={username})'
        conn.search(
            search_base=user_dn_template,
            search_filter=search_filter,
            attributes=[
                username_attr,
                current_app.config['LDAP_EMAIL_ATTRIBUTE'],
                current_app.config['LDAP_FIRSTNAME_ATTRIBUTE'],
                current_app.config['LDAP_LASTNAME_ATTRIBUTE'],
                'memberOf'
            ]
        )
        
        if not conn.entries:
            conn.unbind()
            return None
        
        entry = conn.entries[0]
        
        user_data = {
            'username': username,
            'email': str(entry[current_app.config['LDAP_EMAIL_ATTRIBUTE']]) if hasattr(entry, current_app.config['LDAP_EMAIL_ATTRIBUTE']) else f'{username}@example.com',
            'first_name': str(entry[current_app.config['LDAP_FIRSTNAME_ATTRIBUTE']]) if hasattr(entry, current_app.config['LDAP_FIRSTNAME_ATTRIBUTE']) else username,
            'last_name': str(entry[current_app.config['LDAP_LASTNAME_ATTRIBUTE']]) if hasattr(entry, current_app.config['LDAP_LASTNAME_ATTRIBUTE']) else '',
            'groups': [str(group) for group in entry.memberOf] if hasattr(entry, 'memberOf') else [],
            'distinguished_name': str(entry.entry_dn)
        }
        
        conn.unbind()
        return user_data
    
    @staticmethod
    def _authenticate_ad(username, password):
        """Authenticate against Active Directory"""
        ad_server = current_app.config['AD_SERVER']
        ad_domain = current_app.config['AD_DOMAIN']
        search_base = current_app.config['AD_SEARCH_BASE']
        
        # Create server
        server = Server(ad_server, get_info=ALL)
        
        # Format username for AD (DOMAIN\username)
        ad_username = f'{ad_domain}\\{username}'
        
        # Attempt connection with NTLM
        conn = Connection(
            server,
            user=ad_username,
            password=password,
            authentication=NTLM,
            auto_bind=True
        )
        
        if not conn.bound:
            return None
        
        # Search for user
        search_filter = f'(sAMAccountName={username})'
        conn.search(
            search_base=search_base,
            search_filter=search_filter,
            attributes=[
                'sAMAccountName',
                'mail',
                'givenName',
                'sn',
                'displayName',
                'memberOf',
                'distinguishedName',
                'department',
                'title'
            ]
        )
        
        if not conn.entries:
            conn.unbind()
            return None
        
        entry = conn.entries[0]
        
        user_data = {
            'username': str(entry.sAMAccountName),
            'email': str(entry.mail) if hasattr(entry, 'mail') else f'{username}@{ad_domain.lower()}.com',
            'first_name': str(entry.givenName) if hasattr(entry, 'givenName') else username,
            'last_name': str(entry.sn) if hasattr(entry, 'sn') else '',
            'display_name': str(entry.displayName) if hasattr(entry, 'displayName') else username,
            'department': str(entry.department) if hasattr(entry, 'department') else '',
            'job_title': str(entry.title) if hasattr(entry, 'title') else '',
            'groups': [str(group) for group in entry.memberOf] if hasattr(entry, 'memberOf') else [],
            'distinguished_name': str(entry.distinguishedName)
        }
        
        conn.unbind()
        return user_data
    
    @staticmethod
    def sync_user(username):
        """Sync user information from LDAP/AD"""
        if not current_app.config['LDAP_ENABLED']:
            return None
        
        try:
            # Use service account to query user
            bind_user = current_app.config['LDAP_BIND_USER']
            bind_password = current_app.config['LDAP_BIND_PASSWORD']
            
            if current_app.config['AUTH_TYPE'] == 'ad':
                server = Server(current_app.config['AD_SERVER'], get_info=ALL)
                search_base = current_app.config['AD_SEARCH_BASE']
                search_filter = f'(sAMAccountName={username})'
            else:
                server = Server(
                    current_app.config['LDAP_HOST'],
                    port=current_app.config['LDAP_PORT'],
                    use_ssl=current_app.config['LDAP_USE_SSL'],
                    get_info=ALL
                )
                search_base = current_app.config['LDAP_USER_DN']
                search_filter = f'({current_app.config["LDAP_USERNAME_ATTRIBUTE"]}={username})'
            
            conn = Connection(server, user=bind_user, password=bind_password, auto_bind=True)
            
            conn.search(
                search_base=search_base,
                search_filter=search_filter,
                attributes=['*']
            )
            
            if conn.entries:
                entry = conn.entries[0]
                # Extract user data
                user_data = {
                    'username': username,
                    'email': str(entry.mail) if hasattr(entry, 'mail') else '',
                    'first_name': str(entry.givenName) if hasattr(entry, 'givenName') else '',
                    'last_name': str(entry.sn) if hasattr(entry, 'sn') else '',
                    'groups': [str(group) for group in entry.memberOf] if hasattr(entry, 'memberOf') else []
                }
                conn.unbind()
                return user_data
            
            conn.unbind()
            return None
            
        except Exception as e:
            logger.error(f'LDAP sync failed: {str(e)}')
            return None
    
    @staticmethod
    def map_ad_groups_to_roles(ad_groups):
        """Map AD groups to application roles"""
        # Define mapping (customize based on your AD structure)
        group_role_mapping = {
            'CN=Westval_Admins': 'Admin',
            'CN=Westval_Validators': 'Validator',
            'CN=Westval_QA': 'QA',
            'CN=Westval_Approvers': 'Approver',
            # Add your organization's AD groups here
        }
        
        roles = []
        for group in ad_groups:
            for ad_group, role in group_role_mapping.items():
                if ad_group in group:
                    roles.append(role)
        
        # Default role if no mapping found
        if not roles:
            roles.append('Validator')
        
        return list(set(roles))  # Remove duplicates