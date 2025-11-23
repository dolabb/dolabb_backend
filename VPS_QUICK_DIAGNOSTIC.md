# Quick VPS Web Server Diagnostic

## Problem

Files are uploading successfully, but URLs return "This site can't be reached"
or "took too long to respond".

## Quick Diagnostic Commands

SSH into your VPS:

```bash
ssh dolabbadmin@175.161.178.68.host.secureserver.net
```

Then run these commands one by one:

### 1. Check if Apache is installed and running:

```bash
# Check Apache status
sudo systemctl status apache2
# or (for CentOS/RHEL)
sudo systemctl status httpd

# Check if Apache process is running
ps aux | grep apache
# or
ps aux | grep httpd
```

### 2. Check if web server is listening on port 80:

```bash
sudo netstat -tlnp | grep :80
# or
sudo ss -tlnp | grep :80
```

### 3. Check firewall status:

```bash
# Ubuntu/Debian
sudo ufw status

# CentOS/RHEL
sudo firewall-cmd --list-all
```

### 4. Test web server locally:

```bash
curl http://localhost
curl http://localhost/media/uploads/profiles/
```

## Quick Fix Commands

### If Apache is not running:

**Ubuntu/Debian:**

```bash
sudo systemctl start apache2
sudo systemctl enable apache2
sudo systemctl status apache2
```

**CentOS/RHEL:**

```bash
sudo systemctl start httpd
sudo systemctl enable httpd
sudo systemctl status httpd
```

### If Apache is not installed:

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install apache2
sudo systemctl start apache2
sudo systemctl enable apache2
```

**CentOS/RHEL:**

```bash
sudo yum install httpd
sudo systemctl start httpd
sudo systemctl enable httpd
```

### Open firewall ports:

**Ubuntu/Debian:**

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

**CentOS/RHEL:**

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### Verify Apache config points to public_html:

**Check current document root:**

```bash
# Ubuntu/Debian
grep -r "DocumentRoot" /etc/apache2/sites-available/

# CentOS/RHEL
grep -r "DocumentRoot" /etc/httpd/conf/
```

**Should be:** `/home/dolabbadmin/public_html`

## After Fixing

1. Test from VPS: `curl http://localhost/media/uploads/profiles/`
2. Test from your computer: `http://175.161.178.68/media/uploads/profiles/`
3. Test specific file:
   `http://175.161.178.68/media/uploads/profiles/8af0b735-cd47-499e-b0b3-3522ac32aa0f.JPG`

If these work, then configure DNS for your domain.
