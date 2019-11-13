Docker Aeroo Docs
==================

This is an image that allows you to launch the aeroo docs container

    You should run the image with:
        To run on system boot:
            sudo docker run -p 8989:8989 --name="aeroo_docs" --restart=always -d jobiols/aeroo-docs
        To run manually and delete it on stop:
            sudo docker run -p 8989:8989 --rm -ti jobiols/aeroo-docs


Thanks to Raphaël Valyi (https://github.com/rvalyi), we have taken some 
code from https://github.com/rvalyi/aeroocker

TODO: ADD libreoffice-l10n-es
