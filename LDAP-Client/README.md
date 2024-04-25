# Accessing phpLDSPadmin on Linux:

To access phpLDSPadmin on Linux, I follow these steps:

- First, I install phpLDSPadmin using the command:
  ```
  sudo apt-get install phpldapadmin
  ```

- Then, I start the Apache web server using the command:
  ```
  sudo systemctl start apache2
  ```

- Next, I ensure that the Apache web server is running by executing:
  ```
  sudo systemctl start apache2
  ```

- Additionally, I allow incoming traffic on port 80 (HTTP) using the Uncomplicated Firewall (UFW):
  ```
  sudo ufw allow 80
  ```

- Finally, I access phpLDSPadmin through the web browser using the URL:
  ```
  http://localhost/phpldapadmin
  ```

# Practical Task Implementation:

- ### Creating A New User:
    - To create credentials for our LDAP server, I typically need to add an entry for the admin user to the server's directory. Here's what I'd do:

    - **Creating an LDIF file**: I prepare an LDIF (LDAP Data Interchange Format) file to add a new entry to the LDAP directory. For example:
        ```ldif
        dn: cn=admin,dc=za
        objectClass: simpleSecurityObject
        objectClass: organizationalRole
        cn: admin
        description: Networks LDAP administrator
        userPassword: password
        ```

    - **Executing the Creation Command**:
        ```bash 
        ldapadd -x -D "cn=admin,dc=za" -w password -f admin.ldif
        ```

    - **Searching Command**:
        ```bash
        ldapsearch -x -H ldap://localhost:389 -D "cn=admin,dc=za" -w password -b "dc=za" "(objectClass=*)"
        ```

    - This LDIF file creates a new entry with the DN `cn=admin,dc=za`. The `userPassword` attribute is set to `password`.

    - **Adding the entry to the LDAP directory**: I use the `ldapadd` or `ldapmodify` command to add the entry to the directory. For example:
        ```bash
        ldapadd -x -D "cn=admin,dc=com" -W -f admin.ldif
        ```

- ### Adding Files to LDAP directory:
    - #### `Files`:
        - **Creating the Top Level Domain**:
            ```ldif
            dn: dc=za
            objectClass: top
            objectClass: domain
            dc: za
            ```

        - **Creating the Second Level Domains**:
            ```ldif
            dn: ou=co,dc=za
            objectClass: top
            objectClass: organizationalUnit
            ou: co
            ```

        - **Creating the Organizations**:
            ```ldif
            dn: o=tebogoyungmercykay,ou=co,dc=za
            objectClass: top
            objectClass: organization
            o: tebogoyungmercykay
            ```

        - **Adding the DNS information** (e.g., for "up.ac.za"):
            ```ldif
            dn: cn={5}custom,cn=schema,cn=config
            objectClass: olcSchemaConfig
            cn: {5}custom
            olcAttributeTypes: ( 1.3.6.1.4.1.99999.1 NAME 'myARecord' EQUALITY caseIgnoreMatch SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 SINGLE-VALUE )
            olcAttributeTypes: ( 1.3.6.1.4.1.99999.2 NAME 'myNSRecord' EQUALITY caseIgnoreMatch SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 SINGLE-VALUE )
            olcAttributeTypes: ( 1.3.6.1.4.1.99999.3 NAME 'myMXRecord' EQUALITY caseIgnoreMatch SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 SINGLE-VALUE )
            olcAttributeTypes: ( 1.3.6.1.4.1.99999.5 NAME 'relativeDomainName' EQUALITY caseIgnoreMatch SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 SINGLE-VALUE )
            olcObjectClasses: ( 1.3.6.1.4.1.99999.4 NAME 'myDnsDomain' SUP top STRUCTURAL MUST relativeDomainName MAY ( myARecord $ myNSRecord $ myMXRecord ) )
            ```

    - #### `Commands`:
        ```bash
        ldapadd -x -D "cn=admin,dc=za" -w password -f tld.ldif
        ldapadd -x -D "cn=admin,dc=za" -w password -f second_level_domain.ldif
        ldapadd -x -D "cn=admin,dc=za" -w password -f organization.ldif
        ldapadd -x -D "cn=admin,dc=za" -w password -f dns_info.ldif
        ```