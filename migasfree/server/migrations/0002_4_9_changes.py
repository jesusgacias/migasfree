# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def insert_initial_status_log(apps, schema_editor):
    Computer = apps.get_model('server', 'Computer')
    StatusLog = apps.get_model('server', 'StatusLog')
    db_alias = schema_editor.connection.alias

    for computer in Computer.objects.using(db_alias).all():
        obj = StatusLog()
        obj.computer = computer
        obj.created_at = computer.dateinput
        obj.save()


def delete_all_status_log(apps, schema_editor):
    StatusLog = apps.get_model('server', 'StatusLog')
    db_alias = schema_editor.connection.alias
    StatusLog.objects.using(db_alias).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatusLog',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID'
                )),
                ('status', models.CharField(
                    choices=[
                        (b'intended', 'Intended'),
                        (b'reserved', 'Reserved'),
                        (b'unknown', 'Unknown'),
                        (b'in repair', 'In repair'),
                        (b'available', 'Available'),
                        (b'unsubscribed', 'Unsubscribed')
                    ],
                    default=b'intended',
                    max_length=20,
                    verbose_name='status'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date')),
            ],
            options={
                'verbose_name': 'Status Log',
                'verbose_name_plural': 'Status Logs',
                'permissions': (('can_save_statuslog', 'Can save Status Log'),),
            },
        ),
        migrations.AddField(
            model_name='computer',
            name='status',
            field=models.CharField(
                choices=[
                    (b'intended', 'Intended'),
                    (b'reserved', 'Reserved'),
                    (b'unknown', 'Unknown'),
                    (b'in repair', 'In repair'),
                    (b'available', 'Available'),
                    (b'unsubscribed', 'Unsubscribed')
                ],
                default=b'intended',
                max_length=20,
                verbose_name='status'
            ),
        ),
        migrations.AlterField(
            model_name='attributeset',
            name='attributes',
            field=models.ManyToManyField(
                blank=True,
                help_text='Assigned Attributes',
                to='server.Attribute',
                verbose_name='attributes'
            ),
        ),
        migrations.AlterField(
            model_name='attributeset',
            name='excludes',
            field=models.ManyToManyField(
                blank=True,
                help_text='Excluded Attributes',
                related_name='ExcludeAttributeGroup',
                to='server.Attribute',
                verbose_name='excludes'
            ),
        ),
        migrations.AlterField(
            model_name='computer',
            name='dateinput',
            field=models.DateField(
                auto_now_add=True,
                help_text='Date of input of Computer in migasfree system',
                verbose_name='date input'
            ),
        ),
        migrations.AlterField(
            model_name='computer',
            name='devices_logical',
            field=models.ManyToManyField(blank=True, to='server.DeviceLogical', verbose_name='devices'),
        ),
        migrations.AlterField(
            model_name='computer',
            name='tags',
            field=models.ManyToManyField(blank=True, to='server.Attribute', verbose_name='tags'),
        ),
        migrations.AlterField(
            model_name='devicemodel',
            name='connections',
            field=models.ManyToManyField(blank=True, to='server.DeviceConnection', verbose_name='connections'),
        ),
        migrations.AlterField(
            model_name='faultdef',
            name='attributes',
            field=models.ManyToManyField(blank=True, to='server.Attribute', verbose_name='attributes'),
        ),
        migrations.AlterField(
            model_name='faultdef',
            name='users',
            field=models.ManyToManyField(blank=True, to='server.UserProfile', verbose_name='users'),
        ),
        migrations.AlterField(
            model_name='hwnode',
            name='level',
            field=models.IntegerField(verbose_name='level'),
        ),
        migrations.AlterField(
            model_name='login',
            name='attributes',
            field=models.ManyToManyField(
                blank=True,
                help_text='Sent attributes',
                to='server.Attribute',
                verbose_name='attributes'
            ),
        ),
        migrations.AlterField(
            model_name='message',
            name='computer',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Computer',
                verbose_name='computer'
            ),
        ),
        migrations.AlterField(
            model_name='query',
            name='code',
            field=models.TextField(
                blank=True,
                default=b"query=Package.objects.filter(version=VERSION).filter(Q(repository__id__exact=None))\nfields=('id','name','store__name')\ntitles=('id','name','store')",
                help_text='Django Code: version=user.version, query=QuerySet, fields=list of QuerySet fields names to show, titles=list of QuerySet fields titles',
                null=True,
                verbose_name='code'
            ),
        ),
        migrations.AlterField(
            model_name='query',
            name='parameters',
            field=models.TextField(blank=True, help_text='Django Code', null=True, verbose_name='parameters'),
        ),
        migrations.AlterField(
            model_name='repository',
            name='attributes',
            field=models.ManyToManyField(blank=True, help_text='Assigned Attributes', to='server.Attribute', verbose_name='attributes'),
        ),
        migrations.AlterField(
            model_name='repository',
            name='excludes',
            field=models.ManyToManyField(
                blank=True,
                help_text='Excluded Attributes',
                related_name='ExcludeAttribute',
                to='server.Attribute',
                verbose_name='excludes'
            ),
        ),
        migrations.AlterField(
            model_name='repository',
            name='packages',
            field=models.ManyToManyField(
                blank=True,
                help_text='Assigned Packages',
                to='server.Package',
                verbose_name='Packages/Set'
            ),
        ),
        migrations.AlterField(
            model_name='scheduledelay',
            name='attributes',
            field=models.ManyToManyField(blank=True, to='server.Attribute', verbose_name='attributes'),
        ),
        migrations.AddField(
            model_name='statuslog',
            name='computer',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='server.Computer',
                verbose_name='computer'
            ),
        ),
        migrations.DeleteModel(
            name='Att',
        ),
        migrations.CreateModel(
            name='ClientProperty',
            fields=[
            ],
            options={
                'verbose_name': 'Property',
                'proxy': True,
                'verbose_name_plural': 'Properties',
            },
            bases=('server.property',),
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
            ],
            options={
                'verbose_name': 'Attribute',
                'proxy': True,
                'verbose_name_plural': 'Attributes',
            },
            bases=('server.attribute',),
        ),
        migrations.AlterModelOptions(
            name='attribute',
            options={
                'permissions': (('can_save_attribute', 'Can save Attribute'),),
                'verbose_name': 'Attribute/Tag',
                'verbose_name_plural': 'Attributes/Tags'
            },
        ),
        migrations.AlterModelOptions(
            name='deviceconnection',
            options={
                'permissions': (('can_save_deviceconnection', 'Can save Device Connection'),),
                'verbose_name': 'Connection',
                'verbose_name_plural': 'Connections'
            },
        ),
        migrations.AlterModelOptions(
            name='devicedriver',
            options={
                'permissions': (('can_save_devicedriver', 'Can save Device Driver'),),
                'verbose_name': 'Driver',
                'verbose_name_plural': 'Drivers'
            },
        ),
        migrations.AlterModelOptions(
            name='devicefeature',
            options={
                'permissions': (('can_save_devicefeature', 'Can save Device Feature'),),
                'verbose_name': 'Feature',
                'verbose_name_plural': 'Features'
            },
        ),
        migrations.AlterModelOptions(
            name='devicelogical',
            options={
                'permissions': (('can_save_devicelogical', 'Can save Device Logical'),),
                'verbose_name': 'Device Logical',
                'verbose_name_plural': 'Devices Logical'
            },
        ),
        migrations.AlterModelOptions(
            name='devicemanufacturer',
            options={
                'permissions': (('can_save_devicemanufacturer', 'Can save Device Manufacturer'),),
                'verbose_name': 'Manufacturer',
                'verbose_name_plural': 'Manufacturers'
            },
        ),
        migrations.AlterModelOptions(
            name='devicemodel',
            options={
                'permissions': (('can_save_devicemodel', 'Can save Device Model'),),
                'verbose_name': 'Model',
                'verbose_name_plural': 'Models'
            },
        ),
        migrations.AlterModelOptions(
            name='devicetype',
            options={
                'permissions': (('can_save_devicetype', 'Can save Device Type'),),
                'verbose_name': 'Type',
                'verbose_name_plural': 'Types'
            },
        ),
        migrations.AlterModelOptions(
            name='property',
            options={
                'permissions': (('can_save_property', 'Can save Property'),),
                'verbose_name': 'Property/TagType',
                'verbose_name_plural': 'Properties/TagTypes'
            },
        ),
        migrations.AlterField(
            model_name='devicedriver',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='name'),
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_query SET code=%s, name=%s, parameters=%s WHERE id=3;",
                ["from migasfree.server.models import Login, Computer, Property,Version\nfrom django.db.models import Count\nquery = Login.objects.filter(computer__status__in=Computer.PRODUCTIVE_STATUS)\nif parameters['value'] != '':\n    if str(parameters['exact']) == 'True':\n        query = query.filter(attributes__property_att__id=parameters['property_att'],attributes__value=parameters['value'])\n        fld = 'attributes.filter(property_att__id=parameters[\"property_att\"],value=parameters[\"value\"]).values_list(\"value\",flat=True)'\n    else:\n        query = query.filter(attributes__property_att__id=parameters['property_att'],attributes__value__contains=parameters['value'])\n        fld = 'attributes.filter(property_att__id=parameters[\"property_att\"],value__contains=parameters[\"value\"]).values_list(\"value\",flat=True)'\n    if parameters['version']:\n        query = query.filter(computer__version__id=parameters['version'])\nquery = query.annotate(n=Count('computer'))\nproperty = Property.objects.get(pk=parameters['property_att'])\nfields = ('computer.link', fld, 'computer.version', 'user.link', 'date')\ntitles = ('computer', property.name.lower(), 'version', 'user',  'date of login')", "Production Computers by Attributes...", "def form_params():\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        property_att = forms.ModelChoiceField(Property.objects.all())\n        version = forms.ModelChoiceField(Version.objects.all())\n        value = forms.CharField()\n        exact = forms.ChoiceField( ((False,'No'),(True,'Yes')) )\n    return myForm"]
            )],
            [(
                "UPDATE server_query SET code=%s, name=%s WHERE id=3;",
                ["from migasfree.server.models import Login, Property,Version\nfrom django.db.models import Count\nquery = Login.objects.all()\nif parameters['value'] != '':\n    if str(parameters['exact']) == 'True':\n        query = query.filter(attributes__property_att__id=parameters['property_att'],attributes__value=parameters['value'])\n        fld = 'attributes.filter(property_att__id=parameters[\"property_att\"],value=parameters[\"value\"]).values_list(\"value\",flat=True)'\n    else:\n        query = query.filter(attributes__property_att__id=parameters['property_att'],attributes__value__contains=parameters['value'])\n        fld = 'attributes.filter(property_att__id=parameters[\"property_att\"],value__contains=parameters[\"value\"]).values_list(\"value\",flat=True)'\n    if parameters['version']:\n        query = query.filter(computer__version__id=parameters['version'])\nquery = query.annotate(n=Count('computer'))\nproperty = Property.objects.get(pk=parameters['property_att'])\nfields = ('computer.link', fld, 'computer.version', 'user.link', 'date')\ntitles = ('computer', property.name.lower(), 'version', 'user',  'date of login')", "Computers by Attributes..."]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_query SET code=%s, name=%s WHERE id=4;",
                ["from migasfree.server.models import Computer\nquery = Computer.productives.filter(software__contains=parameters['package']).order_by('datelastupdate')\nfields = ('link', 'ip', 'datelastupdate', 'hw_link')\ntitles = ('Computer', 'ip', 'last update', 'hardware')", "Production Computers with the Package..."]
            )],
            [(
                "UPDATE server_query SET code=%s, name=%s WHERE id=4;",
                ["from migasfree.server.models import Computer\nquery = Computer.objects.filter(software__contains=parameters['package']).order_by('datelastupdate')\nfields = ('link', 'ip', 'datelastupdate', 'hw_link')\ntitles = ('Computer', 'ip', 'last update', 'hardware')", "Computers with the Package..."]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_query SET code=%s WHERE id=5;",
                ["from migasfree.server.models import Package\nfrom django.db.models import Q\nquery = Package.objects.filter(Q(repository__id__exact=None))\nfields = ('version.name', 'store.name', 'link')\ntitles = ('version', 'store', 'package/set')\n"]
            )],
            [(
                "UPDATE server_query SET code=%s WHERE id=5;",
                ["from migasfree.server.models import Package\nfrom django.db.models import Q\nquery = Package.objects.version(0).filter(Q(repository__id__exact=None))\nfields = ('version.name', 'store.name', 'link')\ntitles = ('version', 'store', 'package/set')\n"]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_query SET code=%s, name=%s, parameters=%s WHERE id=7;",
                ["from datetime import datetime, timedelta, date\nfrom migasfree.server.models import Computer\nlast_days = parameters['last_days']\nif last_days <= 0 or last_days == '':\n    last_days = 1\nelse:\n    last_days = int(last_days)\ndelta = timedelta(days=1)\nn = date.today() - ((last_days - 1) * delta)\nquery = Computer.productives.filter(dateinput__gte=n, dateinput__lt=date.today() + delta).order_by('-dateinput')\nfields = ('link', 'version', 'dateinput', 'ip')\ntitles = ('link', 'version', 'dateinput', 'ip')", "Incoming Production Computers...", "def form_params():\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        last_days = forms.CharField()\n    return myForm"]
            )],
            [(
                "UPDATE server_query SET code=%s, name=%s, parameters=%s WHERE id=7;",
                ["from datetime import datetime, timedelta, date\nfrom migasfree.server.models import Computer\nlast_days = parameters['last_days']\nif last_days <= 0 or last_days == '':\n    last_days = 1\nelse:\n    last_days = int(last_days)\ndelta = timedelta(days=1)\nn = date.today() - ((last_days - 1) * delta)\nquery = Computer.objects.filter(dateinput__gte=n, dateinput__lt=date.today() + delta).order_by('-dateinput')\nfields = ('link', 'version', 'dateinput', 'ip')\ntitles = ('link', 'version', 'dateinput', 'ip')", "Incoming Production Computers...", "def form_params():\n    from migasfree.server.forms import ParametersForm\n    from django import forms\n    class myForm(ParametersForm):\n        last_days = forms.CharField()\n    return myForm"]
            )]
        ),
        migrations.RunSQL("DELETE FROM server_query WHERE id=8 OR id=9;", migrations.RunSQL.noop),
        migrations.RunSQL(
            [(
                "UPDATE server_checking SET code=%s WHERE id=2;",
                ["from migasfree.server.models import Fault\nfrom django.db.models import Q\nresult = Fault.objects.filter(checked__exact=0).filter(Q(faultdef__users__id__in=[request.user.id,]) | Q(faultdef__users=None)).count()\nurl = '/admin/server/fault/?checked__exact=0&user=me'\nalert = 'danger'\nmsg = 'Faults to check'\ntarget = 'computer'\n"]
            )],
            [(
                "UPDATE server_checking SET code=%s WHERE id=2;",
                ["from migasfree.server.models import Fault\nfrom migasfree.middleware import threadlocals\nfrom django.db.models import Q\nresult = Fault.objects.filter(checked__exact=0).filter(Q(faultdef__users__id__in=[threadlocals.get_current_user().id,]) | Q(faultdef__users=None)).count()\nurl = '/admin/server/fault/?checked__exact=0&user=me'\nalert = 'danger'\nmsg = 'Faults to check'\ntarget = 'computer'\n"]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_checking SET code=%s WHERE id=3;",
                ["from migasfree.server.models import Package\nfrom django.db.models import Q\nresult = Package.objects.filter(Q(repository__id__exact=None)).count()\nurl = '/query/5/'\nalert = 'warning'\nmsg = 'Package/Set orphan'\ntarget = 'server'\n"]
            )],
            [(
                "UPDATE server_checking SET code=%s WHERE id=3;",
                ["from migasfree.server.models import Package\nfrom django.db.models import Q\nresult = Package.objects.version(0).filter(Q(repository__id__exact=None)).count()\nurl = '/query/5/'\nalert = 'warning'\nmsg = 'Package/Set orphan'\ntarget = 'server'\n"]
            )]
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_checking SET code=%s WHERE id=10;",
                ["import os\nfrom migasfree.settings import MIGASFREE_REPO_DIR\nurl = '/server_messages/'\nalert = 'info'\ntarget = 'server'\nresult=0\nmsg=''\nif os.path.exists(MIGASFREE_REPO_DIR):\n    for _version in os.listdir(MIGASFREE_REPO_DIR):\n        _repos = os.path.join(MIGASFREE_REPO_DIR, _version, 'TMP/REPOSITORIES/dists')\n        if os.path.exists(_repos):\n            for _repo in os.listdir(_repos):\n                result=result+1\n                msg=msg+'%s en %s.' % (_repo, _version)\nmsg = 'Creating %s repositories:%s' % ( result, msg)"]
            )],
            migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_property SET code=%s WHERE prefix='PCI';",
                ["import subprocess\nimport platform\nimport os\n\n_platform = platform.system()\nif _platform == 'Linux' :\n    if os.path.exists('/proc/bus/pci'):\n        cmd_linux=\"\"\"r=''\n      if [ `lspci -n |sed -n 1p|awk '{print $2}'` = 'Class' ]; then\n        dev=`lspci -n |awk '{print $4}'`\n      else\n        dev=`lspci -n |awk '{print $3}'`\n      fi\n      for l in $dev\n      do\n        n=`lspci -d $l|awk '{for (i = 2; i <=NF;++i) print $i}'|tr \"\\n\" \" \"|sed 's/,//g'`\n        r=\"$r$l~$n,\"\n      done\n      echo $r\"\"\"\n        (out,err) = subprocess.Popen( cmd_linux, stdout=subprocess.PIPE, shell=True ).communicate()\n        print out,\n    else:\n        print 'none',\nelif _platform == 'Windows' :\n    print 'none',\n\nelse:\n    print 'none',"]
            )],
            migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            [(
                "UPDATE server_pms SET createrepo=%s WHERE name='apt-get';",
                ["cd %PATH%\ncd ..\nDIST=%REPONAME%\nKEYS=%KEYS%\nARCHS=\"i386 amd64 source\"\nmkdir .cache\nmkdir -p dists/$DIST/PKGS/binary-amd64\nmkdir -p dists/$DIST/PKGS/binary-i386\nmkdir -p dists/$DIST/PKGS/source\ncat > apt-ftparchive.conf <<EOF\nDir {\n ArchiveDir \".\";\n CacheDir \"./.cache\";\n};\nDefault {\n Packages::Compress \". gzip bzip2\";\n Contents::Compress \". gzip bzip2\";\n};\nTreeDefault {\n BinCacheDB \"packages-\\$(SECTION)-\\$(ARCH).db\";\n Directory \"dists/$DIST/\\$(SECTION)\";\n SrcDirectory \"dists/$DIST/\\$(SECTION)\";\n Packages \"\\$(DIST)/\\$(SECTION)/binary-\\$(ARCH)/Packages\";\n Contents \"\\$(DIST)/Contents-\\$(ARCH)\";\n};\nTree \"dists/$DIST\" {\n Sections \"PKGS\";\n Architectures \"i386 amd64 source\";\n}\nEOF\napt-ftparchive generate apt-ftparchive.conf 2> ./err\nif [ $? != 0 ] ; then\n  cat ./err >&2\nfi\nrm ./err\ncat > apt-release.conf <<EOF\nAPT::FTPArchive::Release::Codename \"$DIST\";\nAPT::FTPArchive::Release::Origin \"migasfree\";\nAPT::FTPArchive::Release::Components \"PKGS\";\nAPT::FTPArchive::Release::Label \"migasfree $DISTRO Repository\";\nAPT::FTPArchive::Release::Architectures \"$ARCHS\";\nAPT::FTPArchive::Release::Suite \"$DIST\";\nEOF\napt-ftparchive -c apt-release.conf release dists/$DIST > dists/$DIST/Release\ngpg -u migasfree-repository --homedir $KEYS/.gnupg -abs -o dists/$DIST/Release.gpg dists/$DIST/Release\ngpg -u migasfree-repository --homedir $KEYS/.gnupg --clearsign -o dists/$DIST/InRelease dists/$DIST/Release\nrm -rf apt-release.conf apt-ftparchive.conf\n"]
            )],
            migrations.RunSQL.noop
        ),
        migrations.RunPython(insert_initial_status_log, delete_all_status_log),
    ]
