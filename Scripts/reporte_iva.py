__author__ = 'alan'
# -*- coding: utf-8 -*-
import xmlrpclib
import datetime

user=''
pwd=''
bd=''

class ReporteIva():

    def __init__(self):
        # Get the uid
        self.sock_common = xmlrpclib.ServerProxy ('')
        self.uid = self.sock_common.login(bd, user, pwd)

        #replace localhost with the address of the server
        self.sock = xmlrpclib.ServerProxy('')

    def recuperar_partner(self,id_partner):
        args_partner = [('id', '=', id_partner),('active', '=', 'false'),('active', '=', 'true')]
        ids_partner = self.sock.execute(bd, self.uid, pwd, 'res.partner', 'search', args_partner)
        fields_partner = ['name','document_number']
        data_partner = self.sock.execute(bd, self.uid, pwd, 'res.partner', 'read', ids_partner, fields_partner)
        l_partner = data_partner[0]
        if l_partner['document_number'] == False:
            return (('%s,%s') %(l_partner['name'],'0'))
        else:
            return (('%s,%s') %(l_partner['name'],l_partner['document_number']))


 #   def recuperar_invoiceline_id(self,id_factura):
 #       #Recuperar numero de factura para trabajar con las lineas de facturacion
 #       args_invoiceline = [('invoice_id', '=', id_factura)]
 #       ids_invoiceline = self.sock.execute(bd, self.uid, pwd, 'account.invoice.line', 'search', args_invoiceline)
 #       fields_invoiceline = ['invoice_line_tax_id','name'] #fields to read
 #       data_invoiceline = self.sock.execute(bd, self.uid, pwd, 'account.invoice.line', 'read', ids_invoiceline, fields_invoiceline) #ids is a list of id
 #       for l_invoice_line in data_invoiceline:
 #           self.recuperar_impuesto(l_invoice_line['invoice_line_tax_id'][0])
 #           print('hola')


    def recuperar_impuesto(self,data_line_invoice):
        args_tax = [('invoice_id', '=', data_line_invoice)] #query clause
        ids_tax = self.sock.execute(bd, self.uid, pwd, 'account.invoice.tax', 'search', args_tax)
        fields_tax = ['id', 'base_code_id','name','tax_amount','base_amount'] #fields to read
        data_tax = self.sock.execute(bd, self.uid, pwd, 'account.invoice.tax', 'read', ids_tax, fields_tax) #ids is a list of id
        return data_tax


    def venta(self):
        ##Recuperar las facturas de venta unicamnete
        args = [('date_invoice', '>=', '01/01/2015'),('&'),('date_invoice', '<=', '01/31/2015'),('journal_id', 'like', 'CVB'),('|'),('state','=','open'),('state','=','paid')] #query clause
        ids = self.sock.execute(bd, self.uid, pwd, 'account.invoice', 'search', args)
        fields = ["id",'date_invoice','number','partner_id', 'amount_untaxed',"tax_line","internal_number","amount_total"] #fields to read
        data = self.sock.execute(bd, self.uid, pwd, 'account.invoice', 'read', ids, fields) #ids is a list of id
        reporte_iva_final = open("/home/alan/Escritorio/reporte_iva_venta.ods","a",1)
        reporte_iva_final.write(('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s') %("Fecha Factura","Numero Factura","Cliente","Cuit/Dni","Total","Iva 21%","Iva 10%","Neto","\n"))
        print(data)
        for l_factura in data:
            factura = (('%s') %(l_factura['date_invoice']))
            cliente = self.recuperar_partner(l_factura['partner_id'][0])
            impuestos = self.recuperar_impuesto(l_factura['id'])
            total_iva_21 = 0
            total_iva_10 = 0
            print(l_factura['date_invoice'])
            for lista_impuestos in impuestos:
                if '01003005:V' in lista_impuestos['name']:
                    total_iva_21 = float(float(lista_impuestos['base_amount'])*21)/100
                elif '01003004:V' in lista_impuestos['name']:
                    total_iva_10 = float(float(lista_impuestos['base_amount'])*10.5)/100
            reporte_iva_final.write(('%s,%s,%s,%s,%.2f,%.2f,%.2f,%s') %(l_factura['date_invoice'],l_factura['number'],cliente.encode('utf-8'),l_factura['amount_untaxed'],total_iva_21,total_iva_10,l_factura['amount_total'],"\n"))

        reporte_iva_final.close()


    def compra(self):
        ##Recuperar las facturas de venta unicamnete
        args = [('date_invoice', '>=', '01/01/2015'),('&'),('date_invoice', '<=', '01/31/2015'),('journal_id', 'like', 'CC'),('|'),('state','=','open'),('state','=','paid')] #query clause
        ids = self.sock.execute(bd, self.uid, pwd, 'account.invoice', 'search', args)
        fields = ["id",'date_invoice','number','partner_id', 'amount_untaxed',"tax_line","internal_number","amount_total"] #fields to read
        data = self.sock.execute(bd, self.uid, pwd, 'account.invoice', 'read', ids, fields) #ids is a list of id
        reporte_iva_final_compra = open("/home/alan/Escritorio/reporte_iva_compra.ods","a",1)
        reporte_iva_final_compra.write(('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s') %("Fecha Factura","Numero Factura","Cliente","Cuit/Dni","Total","Iva 27%","Iva 21%","Iva 10%","Sin Iva","Neto","\n"))
        print(data)
        for l_factura in data:
            factura = (('%s') %(l_factura['date_invoice']))
            cliente = self.recuperar_partner(l_factura['partner_id'][0])
            impuestos = self.recuperar_impuesto(l_factura['id'])
            sin_iva = 0
            total_iva_27 = 0
            total_iva_21 = 0
            total_iva_10 = 0

            for lista_impuestos in impuestos:
                print(lista_impuestos['name'])
                if '01003006:C' in lista_impuestos['name']:
                    total_iva_27 = float(float(lista_impuestos['base_amount'])*27)/100
                elif '01003005:C' in lista_impuestos['name']:
                    total_iva_21 = float(float(lista_impuestos['base_amount'])*21)/100
                elif '01003004:C' in lista_impuestos['name']:
                    total_iva_10 = float(float(lista_impuestos['base_amount'])*10)/100
                elif '01003000:C' in lista_impuestos['name']:
                    sin_iva = 0
            reporte_iva_final_compra.write(('%s,%s,%s,%s,%.2f,%.2f,%.2f,%.2f,%.2f,%s') %(l_factura['date_invoice'],l_factura['number'],cliente.encode('utf-8'),l_factura['amount_untaxed'],-total_iva_27,-total_iva_21,-total_iva_10,sin_iva,l_factura['amount_total'],"\n"))

        reporte_iva_final_compra.close()
           #print(('%s,%s,%s,%s') %(factura, cliente,l_factura['amount_untaxed'],iva_porcliente))


ReporteIva().compra()
