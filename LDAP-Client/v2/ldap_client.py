from ldap3 import Server, Connection, ALL

# LDAP server settings
LDAP_SERVER = "localhost"
LDAP_PORT = 389
BASE_DN = "dc=example,dc=za"
ADMIN_DN = "cn=admin,dc=example,dc=za"
ADMIN_PASSWORD = "123"

def ldap_query(org_name):
    server = Server(LDAP_SERVER, port=LDAP_PORT, get_info=ALL)
    conn = Connection(server, user=ADMIN_DN, password=ADMIN_PASSWORD, auto_bind=True)

    # Construct LDAP search filter
    search_filter = f"(dc={org_name.split('.')[0]})"  # Match the first component of the domain

    # Perform LDAP search
    conn.search(BASE_DN, search_filter, attributes=["aRecord", "nsRecord", "mxRecord"])

    # Display search results
    if conn.entries:
        print(f"Resource records for organization '{org_name}':")
        for entry in conn.entries:
            print(f"DN: {entry.entry_dn}")
            for attr in entry.entry_attributes:
                print(f"{attr}: {entry[attr]}")
    else:
        print(f"No resource records found for organization '{org_name}'")

    # Unbind connection
    # conn.unbind()

def main():
    while True:
        org_name = input("Enter organization name (or 'q' to quit): ")
        if org_name.lower() == 'q':
            break
        else:
            ldap_query(org_name)

if __name__ == "__main__":
    main()
