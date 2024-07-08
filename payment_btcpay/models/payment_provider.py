import logging

from odoo import _, api, fields, models
from .libs.client import BTCPayClient
from .libs import crypto

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('btcpay', "BTCPay")], ondelete={'btcpay': 'set default'})

    btcpay_location = fields.Char(string='BTCPay Server URL', size=64, help='URL where your BTCPay Server instance is reachable (where you log into your BTCPay Server).', default='https://testnet.demo.btcpayserver.org')
    btcpay_pairingCode = fields.Char(string='Pairing Code', help='Create paring Code in your BTCPay server and put here')

    btcpay_token = fields.Char(string='Token', help='Access Token to BTCPay. Leave empty, will be autogenerated during pairing.')
    btcpay_privateKey = fields.Text(string='Private Key', help='Private Key for BTCPay Client. Leave empty, will be autogenerated during pairing.')
    btcpay_facade = fields.Char(string='Facade', help='Token facade type: merchant/pos/payroll. Keep merchant', default='merchant')

    def create(self, values_list):
        if self.code == 'btcpay':
            values_list['btcpay_privateKey'] = crypto.generate_privakey()

        return super(PaymentProvider, self).create(values_list)

    @api.onchange('btcpay_pairingCode')
    def _onchange_pairingCode(self):
        if not self.btcpay_token and self.code == 'btcpay' and not self.btcpay_pairingCode == '':
            #_logger.info("ONCHANGE PAIRING CODE***SELF:  %s %s %s", self.btcpay_location, self.btcpay_privateKey, self.btcpay_pairingCode)
            self.btcpay_privateKey = crypto.generate_privkey()
            client = BTCPayClient(host=self.btcpay_location, pem=self.btcpay_privateKey)
            token = client.pair_client(self.btcpay_pairingCode)
            self.btcpay_token = token.get(self.btcpay_facade)

    @api.onchange('btcpay_token')
    def _onchange_token(self):
        if self.code == 'btcpay':
            self.btcpay_pairingCode = ''
            #_logger.info("ONCHANGE TOKEN")


    @api.onchange('btcpay_location')
    def _onchange_location(self):
        if self.code == 'btcpay':
            self.btcpay_token = ''
            #_logger.info("ONCHANGE LOCATION ***SELF:  %s %s %s", self.btcpay_location, self.btcpay_privateKey, self.btcpay_pairingCode)
            self.btcpay_privateKey = ''
            self.btcpay_pairingCode = ''