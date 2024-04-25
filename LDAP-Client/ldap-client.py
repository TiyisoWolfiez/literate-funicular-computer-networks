import ldap3

PORT = 389
TEMP_PASS = 'tebogo63729013'
USERNAME = 'tebogoyungmercykay'

class LdapClient:
    def __init__(self, server, user, password):
        self.server = ldap3.Server(server)
        self.conn = ldap3.Connection(self.server, user, password, auto_bind=True)

    def query(self, base_dn, query):
        self.conn.search(base_dn, query, attributes=ldap3.ALL_ATTRIBUTES)
        return self.conn.entries


def query_all_tld(client, tld = 'za'):
    entries = client.query('dc=za', '(objectClass=*)')
    print("\n\n----------------------------------------")
    print(f"--- All (.{tld}) Top Level Domain Entries: ------")
    print("----------------------------------------")
    for entry in entries:
        print(entry)
        

def query_all_sld(client, sld = 'co'):
    entries = client.query(f'ou={sld},dc=za', '(objectClass=*)')
    print("\n\n----------------------------------------")
    print(f"--- All (.{sld})) Second Level Domain Entries: ---")
    print("----------------------------------------")
    for entry in entries:
        print(entry)
        

def query_all_org_info(client, org = USERNAME, sld = 'co'):
    entries = client.query(f'o={org},ou={sld},dc=za', '(objectClass=dnsDomain)')
    print("\n\n----------------------------------------")
    print(f"--- All Info (.{org}.{sld}) Organisations Entries: ---------")
    print("----------------------------------------")
    for entry in entries:
        print(entry)
        print("\n")
        for attr in entry.entry_attributes:
            print(f"{attr}: {entry[attr]}")
        print("\n")


def add_dns_info(client, org=USERNAME, sld = 'co', a_record='127.0.0.1', ns_record='ns.example.com', mx_record='mx.example.com'):
    dn = f'o={org},ou={sld},dc=za'
    changes = {
        'aRecord': [(ldap3.MODIFY_REPLACE, [a_record])],
        'nSRecord': [(ldap3.MODIFY_REPLACE, [ns_record])],
        'mXRecord': [(ldap3.MODIFY_REPLACE, [mx_record])]
    }
    client.conn.modify(dn, changes)


def add_tld(client, tld='za'):
    dn = f'dc={tld}'
    object_class = ['top', 'domain']
    attributes = {
        'dc': tld
    }
    client.conn.add(dn, object_class, attributes)
    

def add_sld(client, sld='gov'):
    dn = f'ou={sld},dc=za'
    object_class = ['top', 'organizationalUnit']
    attributes = {
        'ou': sld
    }
    client.conn.add(dn, object_class, attributes)


def add_org(client, org='uj', sld='ac'):
    dn = f'o={org},ou={sld},dc=za'
    object_class = ['top', 'organization']
    attributes = {
        'o': org,
        'aRecord': '127.0.0.1',
        'nSRecord': 'ns.example.com',
        'mXRecord': 'mx.example.com'
    }
    client.conn.add(dn, object_class, attributes)
    add_dns_info(client, org, sld)


# Usage
# client = LdapClient(f'ldap://localhost:{PORT}', 'cn=admin,dc=za', TEMP_PASS)
# add_dns_info(client)

# # Some Queries
# query_all_tld(client)
# query_all_sld(client)
# query_all_sld(client, 'ac')
# query_all_sld(client, 'gov')
# query_all_org(client)
# query_all_org(client, org='up', sld = 'ac')
# query_all_org_info(client)
# query_all_org_info(client, org='up', sld = 'ac')

# # Add Entries
# add_sld(client, 'drink')
# add_org(client, 'sprite', 'drink')
# add_org(client, 'code', 'drink')

# print("-----------------------------------------")
# print("--- Testing Some More Inputs ------------")
# query_all_sld(client, 'drink')


# # add_tld(client, 'com')

def main():
    # server = input("Enter LDAP server: ")
    # user = input("Enter LDAP user: ")
    # password = input("Enter LDAP password: ")
    # client = LdapClient(server, user, password)
    
    client = LdapClient(f'ldap://localhost:{PORT}', 'cn=admin,dc=za', TEMP_PASS)

    while True:
        print("\n1. Query TLD")
        print("2. Query SLD")
        print("3. Query Organization Info")
        print("4. Add DNS Info")
        print("5. Add TLD")
        print("6. Add SLD")
        print("7. Add Organization")
        print("8. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            tld = input("Enter TLD: ")
            query_all_tld(client, tld)
        elif choice == '2':
            sld = input("Enter SLD: ")
            query_all_sld(client, sld)
        elif choice == '3':
            org = input("Enter organization: ")
            sld = input("Enter SLD: ")
            query_all_org_info(client, org, sld)
        elif choice == '4':
            org = input("Enter organization: ")
            sld = input("Enter SLD: ")
            a_record = input("Enter A record: ")
            ns_record = input("Enter NS record: ")
            mx_record = input("Enter MX record: ")
            add_dns_info(client, org, sld, a_record, ns_record, mx_record)
        elif choice == '5':
            tld = input("Enter TLD: ")
            add_tld(client, tld)
            query_all_tld(client, tld)
        elif choice == '6':
            sld = input("Enter SLD: ")
            add_sld(client, sld)
            query_all_sld(client, sld)
        elif choice == '7':
            org = input("Enter organization: ")
            sld = input("Enter SLD: ")
            add_org(client, org, sld)
            query_all_org_info(client, org, sld)
        elif choice == '8':
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()