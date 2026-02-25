import { useState, useEffect } from 'react';

export interface PricingConfig {
  country: string;
  countryCode: string;
  currency: string;
  currencySymbol: string;
  trialPrice: number;
  monthlyPrice: number;
  trialPriceFormatted: string;
  monthlyPriceFormatted: string;
}

interface ExchangeRates {
  [currency: string]: number;
}

// Base prices in GBP (pence)
const BASE_PRICES = {
  trial: 100, // £1.00 in pence
  monthly: 1999 // £19.99 in pence
};

// Currency configurations with symbols and formatting
const CURRENCY_CONFIG: Record<string, { symbol: string; decimals: number; format: (amount: number) => string }> = {
  'GBP': { 
    symbol: '£', 
    decimals: 2,
    format: (amount: number) => `£${(amount / 100).toFixed(2)}`
  },
  'USD': { 
    symbol: '$', 
    decimals: 2,
    format: (amount: number) => `$${(amount / 100).toFixed(2)}`
  },
  'EUR': { 
    symbol: '€', 
    decimals: 2,
    format: (amount: number) => `€${(amount / 100).toFixed(2)}`
  },
  'CAD': { 
    symbol: 'C$', 
    decimals: 2,
    format: (amount: number) => `C$${(amount / 100).toFixed(2)}`
  },
  'AUD': { 
    symbol: 'A$', 
    decimals: 2,
    format: (amount: number) => `A$${(amount / 100).toFixed(2)}`
  },
  'INR': { 
    symbol: '₹', 
    decimals: 0,
    format: (amount: number) => `₹${Math.round(amount / 100).toLocaleString('en-IN')}`
  },
  'BDT': { 
    symbol: '৳', 
    decimals: 0,
    format: (amount: number) => `৳${Math.round(amount / 100).toLocaleString()}`
  },
  'PKR': { 
    symbol: '₨', 
    decimals: 0,
    format: (amount: number) => `₨${Math.round(amount / 100).toLocaleString()}`
  },
  'ZAR': { 
    symbol: 'R', 
    decimals: 0,
    format: (amount: number) => `R${Math.round(amount / 100)}`
  }
};

// Country to currency mapping
const COUNTRY_CURRENCY_MAP: Record<string, { country: string; currency: string }> = {
  'GB': { country: 'United Kingdom', currency: 'GBP' },
  'US': { country: 'United States', currency: 'USD' },
  'DE': { country: 'Germany', currency: 'EUR' },
  'FR': { country: 'France', currency: 'EUR' },
  'ES': { country: 'Spain', currency: 'EUR' },
  'IT': { country: 'Italy', currency: 'EUR' },
  'NL': { country: 'Netherlands', currency: 'EUR' },
  'CA': { country: 'Canada', currency: 'CAD' },
  'AU': { country: 'Australia', currency: 'AUD' },
  'IN': { country: 'India', currency: 'INR' },
  'BD': { country: 'Bangladesh', currency: 'BDT' },
  'PK': { country: 'Pakistan', currency: 'PKR' },
  'ZA': { country: 'South Africa', currency: 'ZAR' }
};

// Fallback exchange rates (used if API fails)
const FALLBACK_RATES: ExchangeRates = {
  'USD': 1.27,
  'EUR': 1.15,
  'CAD': 1.86,
  'AUD': 1.95,
  'INR': 119,
  'BDT': 160,
  'PKR': 374,
  'ZAR': 24
};

// Fetch current exchange rates from frankfurter.app
const fetchExchangeRates = async (): Promise<ExchangeRates> => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    
    const response = await fetch('https://api.frankfurter.app/latest?from=GBP', {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    
    if (response.ok) {
      const data = await response.json();
      return data.rates;
    }
  } catch (e) {
    console.log('Exchange rate API failed, using fallback rates:', e);
  }
  
  return FALLBACK_RATES;
};

// pricing config based on country and exchange rates
const generatePricingConfig = (countryCode: string, exchangeRates: ExchangeRates): PricingConfig => {
  const countryInfo = COUNTRY_CURRENCY_MAP[countryCode];
  if (!countryInfo) {
    // Return GBP pricing for unknown countries
    const gbpConfig = CURRENCY_CONFIG['GBP'];
    return {
      country: 'United Kingdom',
      countryCode: 'GB',
      currency: 'GBP',
      currencySymbol: gbpConfig.symbol,
      trialPrice: BASE_PRICES.trial,
      monthlyPrice: BASE_PRICES.monthly,
      trialPriceFormatted: gbpConfig.format(BASE_PRICES.trial),
      monthlyPriceFormatted: gbpConfig.format(BASE_PRICES.monthly)
    };
  }

  const currency = countryInfo.currency;
  const currencyConfig = CURRENCY_CONFIG[currency];
  
  if (currency === 'GBP') {
    // Base GBP pricing
    return {
      country: countryInfo.country,
      countryCode: countryCode,
      currency: currency,
      currencySymbol: currencyConfig.symbol,
      trialPrice: BASE_PRICES.trial,
      monthlyPrice: BASE_PRICES.monthly,
      trialPriceFormatted: currencyConfig.format(BASE_PRICES.trial),
      monthlyPriceFormatted: currencyConfig.format(BASE_PRICES.monthly)
    };
  }

  // Convert from GBP to local currency
  const exchangeRate = exchangeRates[currency] || FALLBACK_RATES[currency] || 1;
  const trialPrice = Math.round(BASE_PRICES.trial * exchangeRate);
  const monthlyPrice = Math.round(BASE_PRICES.monthly * exchangeRate);

  return {
    country: countryInfo.country,
    countryCode: countryCode,
    currency: currency,
    currencySymbol: currencyConfig.symbol,
    trialPrice: trialPrice,
    monthlyPrice: monthlyPrice,
    trialPriceFormatted: currencyConfig.format(trialPrice),
    monthlyPriceFormatted: currencyConfig.format(monthlyPrice)
  };
};

// Default to UK pricing if country not found
const DEFAULT_PRICING = generatePricingConfig('GB', FALLBACK_RATES);

export const useLocationPricing = () => {
  const [pricing, setPricing] = useState<PricingConfig>(DEFAULT_PRICING);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const detectLocation = async () => {
      try {
        setLoading(true);
        setError(null);

        // Try to get location from multiple sources
        let countryCode = null;

        // Method 1: Try to get from timezone
        try {
          const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
          const timezoneToCountry: Record<string, string> = {
            'Europe/London': 'GB',
            'America/New_York': 'US',
            'America/Los_Angeles': 'US',
            'America/Chicago': 'US',
            'Europe/Berlin': 'DE',
            'Europe/Paris': 'FR',
            'Europe/Madrid': 'ES',
            'Europe/Rome': 'IT',
            'Europe/Amsterdam': 'NL',
            'America/Toronto': 'CA',
            'Australia/Sydney': 'AU',
            'Asia/Kolkata': 'IN',
            'Asia/Dhaka': 'BD',
            'Africa/Johannesburg': 'ZA'
          };
          countryCode = timezoneToCountry[timezone];
        } catch (e) {
          console.log('Timezone detection failed:', e);
        }

        // Method 2: Try IP-based geolocation if timezone didn't work
        if (!countryCode) {
          try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);
            
            const response = await fetch('https://ipapi.co/json', {
              signal: controller.signal
            });
            clearTimeout(timeoutId);
            
            if (response.ok) {
              const data = await response.json();
              countryCode = data.country_code;
            }
          } catch (e) {
            console.log('IP geolocation failed:', e);
          }
        }

        // Method 3: Try alternative IP service
        if (!countryCode) {
          try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);
            
            const response = await fetch('https://api.country.is/', {
              signal: controller.signal
            });
            clearTimeout(timeoutId);
            
            if (response.ok) {
              const data = await response.json();
              countryCode = data.country;
            }
          } catch (e) {
            console.log('Alternative IP service failed:', e);
          }
        }

        // Fetch exchange rates and generate pricing
        const exchangeRates = await fetchExchangeRates();
        const detectedPricing = countryCode && COUNTRY_CURRENCY_MAP[countryCode]
          ? generatePricingConfig(countryCode, exchangeRates)
          : DEFAULT_PRICING;

        setPricing(detectedPricing);
        
        console.log('Location pricing detected:', {
          countryCode,
          pricing: detectedPricing
        });

      } catch (err) {
        console.error('Error detecting location:', err);
        setError('Failed to detect location, using default pricing');
        setPricing(DEFAULT_PRICING);
      } finally {
        setLoading(false);
      }
    };

    detectLocation();
  }, []);

  return {
    pricing,
    loading,
    error,
    isDefault: pricing.countryCode === DEFAULT_PRICING.countryCode
  };
};