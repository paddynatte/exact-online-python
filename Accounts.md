Exact Online REST API - Accounts
Endpoint
Accounts

Good to know
This entity supports webhooks.


This API allows to filter only on specific fields. Below you can see per field if it can be filtered on or not.
When you filter on a key field, there are two syntaxes possible which are both supported. In the example usage section you can see the two syntaxes which are supported.

Scope
Crm accounts

URI
/api/v1/{division}/crm/Accounts


GET  POST  PUT  DELETE
Example usage
/api/v1/{division}/crm/Accounts?$filter=ID eq guid'00000000-0000-0000-0000-000000000000'&$select=Accountant

/api/v1/{division}/crm/Accounts(guid'00000000-0000-0000-0000-000000000000')?$select=Accountant


Properties
Name ↑↓	Type ↑↓	Webhook ↑↓	Filter ↑↓	Description ↑↓
	ID 	Edm.Guid		Mandatory filter	Primary key
	Accountant	Edm.Guid	Supports webhook	Mandatory filter	Reference to the accountant of the customer. Conditions: The referred accountant must have value > 0 in the field IsAccountant
	AccountManager	Edm.Guid	Supports webhook	Mandatory filter	ID of the account manager
	AccountManagerFullName	Edm.String			Name of the account manager
	AccountManagerHID	Edm.Int32			Number of the account manager
	ActivitySector	Edm.Guid	Supports webhook		Reference to Activity sector of the account
	ActivitySubSector	Edm.Guid	Supports webhook		Reference to Activity sub-sector of the account
	AddressLine1	Edm.String	Supports webhook	Mandatory filter	Visit address first line
	AddressLine2	Edm.String	Supports webhook	Mandatory filter	Visit address second line
	AddressLine3	Edm.String	Supports webhook	Mandatory filter	Visit address third line
	AutomaticProcessProposedEntry	Edm.Byte	Supports webhook		Automatically create entries for complete entry proposals
	BankAccounts	
BankAccounts
Collection of Bank accounts
	Blocked	Edm.Boolean	Supports webhook	Mandatory filter	Indicates if the account is blocked
	BRIN	Edm.Guid	Supports webhook	Mandatory filter	Obsolete
	BSN	Edm.String		Mandatory filter	Citizen Service Number for the Netherlands
	BusinessType	Edm.Guid	Supports webhook		Reference to the business type of the account
	CanDropShip	Edm.Boolean	Supports webhook		Indicates the default for the possibility to drop ship when an item is linked to a supplier
	ChamberOfCommerce	Edm.String	Supports webhook	Mandatory filter	Chamber of commerce number
	City	Edm.String	Supports webhook	Mandatory filter	Visit address City
	Classification	Edm.String		Mandatory filter	Obsolete
	Classification1	Edm.Guid		Mandatory filter	Account classification 1
	Classification2	Edm.Guid		Mandatory filter	Account classification 2
	Classification3	Edm.Guid		Mandatory filter	Account classification 3
	Classification4	Edm.Guid		Mandatory filter	Account classification 4
	Classification5	Edm.Guid		Mandatory filter	Account classification 5
	Classification6	Edm.Guid		Mandatory filter	Account classification 6
	Classification7	Edm.Guid		Mandatory filter	Account classification 7
	Classification8	Edm.Guid		Mandatory filter	Account classification 8
	ClassificationDescription	Edm.String			Obsolete
	Code	Edm.String	Supports webhook	Mandatory filter	Unique key, fixed length numeric string with leading spaces, length 18. IMPORTANT: When you use OData $filter on this field you have to make sure the filter parameter contains the leading spaces
	CodeAtSupplier	Edm.String	Supports webhook	Mandatory filter	Code under which your own company is known at the account
	CompanySize	Edm.Guid	Supports webhook		Reference to Company size of the account
	ConsolidationScenario	Edm.Byte	Supports webhook		Consolidation scenario (Time & Billing). Values: 0 = No consolidation, 1 = Item, 2 = Item + Project, 3 = Item + Employee, 4 = Item + Employee + Project, 5 = Project + WBS + Item, 6 = Project + WBS + Item + Employee. Item means in this case including Unit and Price, these also have to be the same to consolidate
	ControlledDate	Edm.DateTime	Supports webhook		Date of the latest control of account data with external web service
	Costcenter	Edm.String	Supports webhook		Obsolete
	CostcenterDescription	Edm.String			Obsolete
	CostPaid	Edm.Byte	Supports webhook		Obsolete
	Country	Edm.String	Supports webhook	Mandatory filter	Country code
	CountryName	Edm.String			Country name
	Created	Edm.DateTime		Mandatory filter	Creation date
	Creator	Edm.Guid			User ID of creator
	CreatorFullName	Edm.String			Name of creator
	CreditLinePurchase	Edm.Double	Supports webhook		Maximum amount of credit for Purchase. If no value has been defined, there is no credit limit
	CreditLineSales	Edm.Double	Supports webhook		Maximum amount of credit for sales. If no value has been defined, there is no credit limit
	Currency	Edm.String	Supports webhook		Obsolete
	CustomerSince	Edm.DateTime	Supports webhook		Obsolete
	CustomField	Edm.String			Custom field endpoint. Provided only for the Exact Online Premium users.
	DatevCreditorCode	Edm.String			DATEV creditor code for Germany legislation
	DatevDebtorCode	Edm.String			DATEV debtor code for Germany legislation
	DeliveryAdvice	Edm.Byte			Indicates how deliveries are handled. Values: 0 = Partial, orders can be delivered partial, 1 = Complete the order needs to be complete to deliver, 2 = Partial without backorder when deliver partially the remainder of the order is completed without delivery
	DiscountPurchase	Edm.Double	Supports webhook		Default discount percentage for purchase. This is stored as a fraction. ie 5.5% is stored as .055
	DiscountSales	Edm.Double	Supports webhook		Default discount percentage for sales. This is stored as a fraction. ie 5.5% is stored as .055
	Division	Edm.Int32	Supports webhook		Division code
	Document	Edm.Guid	Supports webhook		Obsolete
	DunsNumber	Edm.String	Supports webhook		Obsolete
	Email	Edm.String	Supports webhook	Mandatory filter	E-Mail address of the account
	EnableSalesPaymentLink	Edm.Boolean			Indicates whether payment link is activated for sales
	EndDate	Edm.DateTime	Supports webhook	Mandatory filter	Determines in combination with the start date if the account is active. If the current date is > end date the account is inactive
	EORINumber	Edm.String		Mandatory filter	EORI number
	EstablishedDate	Edm.DateTime	Supports webhook		RegistrationDate
	Fax	Edm.String	Supports webhook	Mandatory filter	Fax number
	GLAccountPurchase	Edm.Guid	Supports webhook		Default (corporate) GL offset account for purchase (cost)
	GLAccountSales	Edm.Guid	Supports webhook		Default (corporate) GL offset account for sales (revenue)
	GLAP	Edm.Guid	Supports webhook		Default GL account for Accounts Payable
	GLAR	Edm.Guid	Supports webhook		Default GL account for Accounts Receivable
	GlnNumber	Edm.String	Supports webhook		Global Location Number can be used by companies to identify their locations, giving them complete flexibility to identify any type or level of location required
	HasWithholdingTaxSales	Edm.Boolean			Indicates whether a customer has withholding tax on sales
	IgnoreDatevWarningMessage	Edm.Boolean			Suppressed warning message when there is duplication on the DATEV code
	IncotermAddressPurchase	Edm.String			Address of Incoterm for Purchase
	IncotermAddressSales	Edm.String			Address of Incoterm for Sales
	IncotermCodePurchase	Edm.String			Code of Incoterm for Purchase
	IncotermCodeSales	Edm.String			Code of Incoterm for Sales
	IncotermVersionPurchase	Edm.Int16			Version of Incoterm for Purchase
Supported version for Incoterms : 2010, 2020
	IncotermVersionSales	Edm.Int16			Version of Incoterm for Sales
Supported version for Incoterms : 2010, 2020
	IntraStatArea	Edm.String	Supports webhook		Intrastat Area
	IntraStatDeliveryTerm	Edm.String	Supports webhook		Intrastat delivery method
	IntraStatSystem	Edm.String	Supports webhook		System for Intrastat
	IntraStatTransactionA	Edm.String	Supports webhook		Transaction type A for Intrastat
	IntraStatTransactionB	Edm.String	Supports webhook		Transaction type B for Intrastat
	IntraStatTransportMethod	Edm.String	Supports webhook		Transport method for Intrastat
	InvoiceAccount	Edm.Guid	Supports webhook	Mandatory filter	ID of account to be invoiced instead of this account
	InvoiceAccountCode	Edm.String			Code of InvoiceAccount
	InvoiceAccountName	Edm.String			Name of InvoiceAccount
	InvoiceAttachmentType	Edm.Int32	Supports webhook		Indicates which attachment types should be sent when a sales invoice is printed. Only values in related table with Invoice=1 are allowed
	InvoicingMethod	Edm.Int32	Supports webhook		Method of sending for sales invoices. Values: 1: Paper, 2: EMail, 4: Mailbox (electronic exchange), 8: Send and track, 32: Send via Peppol
Take notes: To use the '4 - Mailbox (electronic exchange)' option, the 'Mailbox' feature set is required in the licence. To use the '32 - Send via Peppol' option, e-invoicing via Peppol must be activated

	IsAccountant	Edm.Byte	Supports webhook	Mandatory filter	Indicates whether the account is an accountant. Values: 0 = No accountant, 1 = True, but accountant doesn't want his name to be published in the list of accountants, 2 = True, and accountant is published in the list of accountants
	IsAgency	Edm.Byte	Supports webhook		Indicates whether the accounti is an agency
	IsAnonymised	Edm.Byte			Indicates whtether the account is anonymised.
	IsBank	Edm.Boolean	Supports webhook		Obsolete
	IsCompetitor	Edm.Byte	Supports webhook		Indicates whether the account is a competitor
	IsExtraDuty	Edm.Boolean			Indicates whether a customer is eligible for extra duty
	IsMailing	Edm.Byte	Supports webhook		Indicates if the account is excluded from mailing marketing information
	IsMember	Edm.Boolean	Supports webhook		Obsolete
	IsPilot	Edm.Boolean	Supports webhook		Indicates whether the account is a pilot account
	IsPurchase	Edm.Boolean	Supports webhook		Obsolete
	IsReseller	Edm.Boolean	Supports webhook	Mandatory filter	Indicates whether the account is a reseller
	IsSales	Edm.Boolean	Supports webhook	Mandatory filter	Indicates whether the account is allowed for sales
	IsSupplier	Edm.Boolean	Supports webhook	Mandatory filter	Indicates whether the account is a supplier
	Language	Edm.String	Supports webhook		Language code
	LanguageDescription	Edm.String			Language description
	Latitude	Edm.Double	Supports webhook		Latitude (used by Google maps)
	LeadPurpose	Edm.Guid	Supports webhook		Reference to Lead purpose of an account
	LeadSource	Edm.Guid	Supports webhook		Reference to Lead source of an account
	Logo	Edm.Binary	Supports webhook		Bytes of the logo image
	LogoFileName	Edm.String	Supports webhook		The file name (without path, but with extension) of the image
	LogoThumbnailUrl	Edm.String			Thumbnail url of the logo
	LogoUrl	Edm.String			Url to retrieve the logo
	Longitude	Edm.Double	Supports webhook		Longitude (used by Google maps)
	MainContact	Edm.Guid	Supports webhook	Mandatory filter	Reference to main contact person
	Modified	Edm.DateTime	Supports webhook	Mandatory filter	Last modified date
	Modifier	Edm.Guid			User ID of modifier
	ModifierFullName	Edm.String			Name of modifier
	Name	Edm.String	Supports webhook	Mandatory filter	Account name
	OINNumber	Edm.String			Dutch government identification number
	Parent	Edm.Guid	Supports webhook	Mandatory filter	ID of the parent account
	PayAsYouEarn	Edm.String			Indicates the loan repayment plan for UK legislation
	PaymentConditionPurchase	Edm.String	Supports webhook		Code of default payment condition for purchase
	PaymentConditionPurchaseDescription	Edm.String			Description of PaymentConditionPurchase
	PaymentConditionSales	Edm.String	Supports webhook		Code of default payment condition for sales
	PaymentConditionSalesDescription	Edm.String			Description of PaymentConditionSales
	PeppolIdentifier	Edm.String			Peppol identifier user entered manually, corresponds to picked peppol adress
	PeppolIdentifierType	Edm.Int32			Peppol identifier type that user picked manually - GLN, COC, etc
	Phone	Edm.String	Supports webhook	Mandatory filter	Phone number
	PhoneExtension	Edm.String	Supports webhook		Phone number extention
	Postcode	Edm.String	Supports webhook	Mandatory filter	Visit address postcode
	PriceList	Edm.Guid	Supports webhook	Mandatory filter	Default sales price list for account
	PurchaseCurrency	Edm.String	Supports webhook		Currency of purchase

Take notes: If the currency code input is not in the active currencies, the value will be set to empty.

	PurchaseCurrencyDescription	Edm.String			Description of PurchaseCurrency
	PurchaseLeadDays	Edm.Int32	Supports webhook		Indicates number of days required to receive a purchase. Acts as a default
	PurchaseVATCode	Edm.String	Supports webhook		Default VAT code used for purchase entries
	PurchaseVATCodeDescription	Edm.String			Description of PurchaseVATCode
	RecepientOfCommissions	Edm.Boolean	Supports webhook		Define the relation that should be taken in the official document of the rewarding fiscal fiches Belcotax
	Remarks	Edm.String			Remarks
	Reseller	Edm.Guid	Supports webhook	Mandatory filter	ID of the reseller account. Conditions: the target account must have the property IsReseller turned on
	ResellerCode	Edm.String			Code of Reseller
	ResellerName	Edm.String			Name of Reseller
	RSIN	Edm.String	Supports webhook	Mandatory filter	Fiscal number for NL legislation
	SalesCurrency	Edm.String	Supports webhook		Currency of Sales used for Time & Billing

Take notes: If the currency code input is not in the active currencies, the value will be set to empty.

	SalesCurrencyDescription	Edm.String			Description of SalesCurrency
	SalesTaxSchedule	Edm.Guid			Obsolete
	SalesTaxScheduleCode	Edm.String			Obsolete
	SalesTaxScheduleDescription	Edm.String			Obsolete
	SalesVATCode	Edm.String	Supports webhook		Default VAT code for a sales entry
	SalesVATCodeDescription	Edm.String			Description of SalesVATCode
	SearchCode	Edm.String	Supports webhook	Mandatory filter	Search code
	SecurityLevel	Edm.Int32	Supports webhook		Security level (0 - 100)
	SeparateInvPerSubscription	Edm.Byte	Supports webhook		Indicates how invoices are generated from subscriptions. 0 = subscriptions belonging to the same customer are combined in a single invoice. 1 = each subscription results in one invoice. In both cases, each individual subscription line results in one invoice line
	ShippingLeadDays	Edm.Int32	Supports webhook		Indicates the number of days it takes to send goods to the customer. Acts as a default
	ShippingMethod	Edm.Guid	Supports webhook		Default shipping method
	ShowRemarkForSales	Edm.Boolean			Indicates whether to display Ordered by account's remarks when creating a new sales order
	StartDate	Edm.DateTime	Supports webhook	Mandatory filter	Indicates in combination with the end date if the account is active
	State	Edm.String	Supports webhook		State/Province/County code When changing the Country and the State is filled, the State must be assigned with a valid value from the selected country or set to empty
	StateName	Edm.String			Name of State
	Status	Edm.String	Supports webhook	Mandatory filter	If the status field is filled this means the account is a customer. The value indicates the customer status. Possible values: A=None, S=Suspect, P=Prospect, C=Customer
	StatusSince	Edm.DateTime	Supports webhook		Obsolete
	TradeName	Edm.String	Supports webhook		Trade name can be registered and shown with the client (for all legislations)
	Type	Edm.String	Supports webhook	Mandatory filter	Account type: Values: A = Relation, D = Division
	UniqueTaxpayerReference	Edm.String			Unique taxpayer reference for UK legislation
	VATLiability	Edm.String	Supports webhook		Indicates the VAT status of an account to be able to identify the relation that should be selected in the VAT debtor listing in Belgium
	VATNumber	Edm.String	Supports webhook	Mandatory filter	The number under which the account is known at the Value Added Tax collection agency
	Website	Edm.String	Supports webhook		Website of the account