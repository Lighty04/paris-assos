#!/usr/bin/env python3
"""
Net Subvention Calculator

Calculates true taxpayer contributions by reconciling:
- acompte + solde (parts of same commitment)
- subtracting remboursements (return of funds)
- excluding emprunt repayments
- handling régularisations appropriately

Outputs: data_net.json with net_subvention fields and data quality metrics
"""

import json
import re
from collections import defaultdict
from typing import Dict, List, Any, Tuple


def classify_subvention(obj: str) -> str:
    """Classify subvention type based on object text"""
    obj_upper = obj.upper()
    
    # Check for emprunt first (exclude these)
    if 'EMPRUNT' in obj_upper and ('REMBOURSEMENT' in obj_upper or 'REMBOURS' in obj_upper):
        return 'emprunt_repayment'
    
    # Check for remboursement (subtract these)
    if 'REMBOURSEMENT' in obj_upper or 'REMBOURS' in obj_upper:
        return 'remboursement'
    
    # Check for régularisation
    if 'RÉGULARISATION' in obj_upper or 'REGULARISATION' in obj_upper:
        return 'regularisation'
    
    # Check for acompte
    if 'ACOMPT' in obj_upper or 'A COMPT' in obj_upper:
        return 'acompte'
    
    # Check for solde
    if 'SOLD' in obj_upper and not 'SOLDAT' in obj_upper:
        return 'solde'
    
    # Default: normal subvention
    return 'subvention'


def calculate_net_subvention(entries: List[Dict]) -> Tuple[float, Dict]:
    """
    Calculate net subvention for a group of entries in the same year.
    
    Returns:
        (net_amount, metadata)
    """
    if not entries:
        return 0.0, {'flags': ['no_entries']}
    
    # Group by type
    by_type = defaultdict(list)
    for entry in entries:
        sub_type = classify_subvention(entry.get('object', ''))
        by_type[sub_type].append(entry)
    
    has_acompte = len(by_type['acompte']) > 0
    has_solde = len(by_type['solde']) > 0
    
    net = 0.0
    components = {
        'acompte': 0.0,
        'solde': 0.0,
        'subvention': 0.0,
        'regularisation': 0.0,
        'remboursement': 0.0,
        'emprunt_repayment': 0.0
    }
    flags = []
    
    # Calculate components
    for entry in by_type['acompte']:
        components['acompte'] += entry['amount']
    
    for entry in by_type['solde']:
        components['solde'] += entry['amount']
    
    for entry in by_type['subvention']:
        components['subvention'] += entry['amount']
    
    for entry in by_type['regularisation']:
        # Regularisations can be positive or negative
        # We'll treat them as-is for now
        components['regularisation'] += entry['amount']
    
    for entry in by_type['remboursement']:
        components['remboursement'] -= entry['amount']  # Subtract
    
    for entry in by_type['emprunt_repayment']:
        components['emprunt_repayment'] += entry['amount']  # Track but exclude
    
    # Calculate net
    # Special case: If year has both acompte AND solde, they are parts of same commitment
    # So we include both (don't double count - they ARE separate payments of same commitment)
    net = (components['acompte'] + components['solde'] + 
           components['subvention'] + components['regularisation'] + 
           components['remboursement'])  # Already negative
    
    # Data quality flags
    if has_acompte and not has_solde:
        flags.append('incomplete_acompte_no_solde')
    
    if net < 0:
        flags.append('negative_net')
    
    if len(entries) > 10:
        flags.append('many_entries')
    
    metadata = {
        'components': components,
        'entry_count': len(entries),
        'types': {k: len(v) for k, v in by_type.items()},
        'flags': flags,
        'has_acompte': has_acompte,
        'has_solde': has_solde
    }
    
    return net, metadata


def find_duplicates(year_entries: List[Dict]) -> List[int]:
    """Find potential duplicate entries (same description, similar amount)"""
    duplicates = []
    seen = {}  # description -> [indices]
    
    for i, entry in enumerate(year_entries):
        obj = entry.get('object', '').strip().upper()
        amount = entry.get('amount', 0)
        
        # Simple duplicate detection: same description within 1% amount
        if obj in seen:
            for j, prev_amount in seen[obj]:
                # Check if amounts are within 1%
                if prev_amount > 0 and abs(amount - prev_amount) / prev_amount < 0.01:
                    duplicates.append(i)
                    break
            seen[obj].append((i, amount))
        else:
            seen[obj] = [(i, amount)]
    
    return duplicates


def process_association(assoc: Dict) -> Tuple[Dict, Dict]:
    """
    Process an association to calculate net subventions.
    
    Returns:
        (processed_association, quality_metrics)
    """
    processed = assoc.copy()
    subventions = assoc.get('subventions', [])
    
    # Group by year
    by_year = defaultdict(list)
    for sub in subventions:
        year = sub.get('year', '')
        if year:
            by_year[year].append(sub)
    
    # Calculate net for each year
    net_subventions = []
    year_metadata = {}
    
    for year in sorted(by_year.keys()):
        year_entries = by_year[year]
        net, metadata = calculate_net_subvention(year_entries)
        
        # Check for duplicates
        duplicates = find_duplicates(year_entries)
        if duplicates:
            metadata['flags'].append(f'potential_duplicates:{len(duplicates)}')
        metadata['duplicates'] = duplicates
        
        net_subventions.append({
            'year': year,
            'net_amount': net,
            'raw_amount': sum(e['amount'] for e in year_entries),
            'entry_count': len(year_entries),
            'flags': metadata['flags'],
            'components': metadata['components']
        })
        year_metadata[year] = metadata
    
    # Calculate totals
    total_net = sum(ns['net_amount'] for ns in net_subventions)
    total_raw = sum(ns['raw_amount'] for ns in net_subventions)
    
    processed['netSubventions'] = net_subventions
    processed['netTotalAmount'] = total_net
    processed['netYearlyData'] = {year: data['net_amount'] for year, data in 
                                   [(ns['year'], ns) for ns in net_subventions]}
    
    # Quality metrics for this association
    quality = {
        'total_years': len(by_year),
        'years_with_incomplete': sum(1 for y, m in year_metadata.items() 
                                      if 'incomplete_acompte_no_solde' in m['flags']),
        'years_with_negative': sum(1 for y, m in year_metadata.items() 
                                    if 'negative_net' in m['flags']),
        'years_with_many_entries': sum(1 for y, m in year_metadata.items() 
                                         if 'many_entries' in m['flags']),
        'years_with_duplicates': sum(1 for y, m in year_metadata.items() 
                                      if m.get('duplicates')),
        'total_net': total_net,
        'total_raw': total_raw,
        'difference': total_raw - total_net,
        'reduction_percent': ((total_raw - total_net) / total_raw * 100) if total_raw > 0 else 0
    }
    
    return processed, quality


def main():
    print("Loading data.json...")
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} associations")
    
    # Process all associations
    processed_data = []
    quality_metrics = []
    
    for i, assoc in enumerate(data):
        processed, quality = process_association(assoc)
        processed_data.append(processed)
        quality_metrics.append(quality)
        
        if (i + 1) % 1000 == 0:
            print(f"Processed {i + 1}/{len(data)} associations...")
    
    # Calculate global statistics
    total_associations = len(processed_data)
    total_net_global = sum(a['netTotalAmount'] for a in processed_data)
    total_raw_global = sum(a.get('totalAmount', 0) for a in processed_data)
    
    # Data quality stats
    years_with_incomplete = sum(q['years_with_incomplete'] for q in quality_metrics)
    years_with_negative = sum(q['years_with_negative'] for q in quality_metrics)
    years_with_duplicates = sum(q['years_with_duplicates'] for q in quality_metrics)
    total_years = sum(q['total_years'] for q in quality_metrics)
    
    clean_years = total_years - years_with_incomplete - years_with_negative - years_with_duplicates
    data_quality_percent = (clean_years / total_years * 100) if total_years > 0 else 0
    
    # Associations with significant adjustments
    associations_with_reduction = sum(1 for q in quality_metrics if q['reduction_percent'] > 5)
    
    stats = {
        'totalAssociations': total_associations,
        'totalNetAmount': total_net_global,
        'totalRawAmount': total_raw_global,
        'difference': total_raw_global - total_net_global,
        'reductionPercent': ((total_raw_global - total_net_global) / total_raw_global * 100) 
                           if total_raw_global > 0 else 0,
        'dataQuality': {
            'totalYears': total_years,
            'cleanYears': clean_years,
            'suspiciousYears': total_years - clean_years,
            'cleanPercent': round(data_quality_percent, 2),
            'yearsWithIncomplete': years_with_incomplete,
            'yearsWithNegative': years_with_negative,
            'yearsWithDuplicates': years_with_duplicates,
            'associationsWithReduction': associations_with_reduction
        }
    }
    
    # Save processed data
    output = {
        'stats': stats,
        'associations': processed_data
    }
    
    print("\nSaving data_net.json...")
    with open('data_net.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("NET SUBVENTION CALCULATION COMPLETE")
    print("="*60)
    print(f"\nTotal Associations: {total_associations:,}")
    print(f"Total Net Amount:   {total_net_global:,.0f} €")
    print(f"Total Raw Amount:   {total_raw_global:,.0f} €")
    print(f"Difference:         {total_raw_global - total_net_global:,.0f} €")
    print(f"Reduction:          {((total_raw_global - total_net_global) / total_raw_global * 100):.1f}%")
    print(f"\nData Quality:")
    print(f"  Total Years:      {total_years:,}")
    print(f"  Clean Years:      {clean_years:,} ({data_quality_percent:.1f}%)")
    print(f"  Incomplete Data:  {years_with_incomplete:,}")
    print(f"  Negative Nets:    {years_with_negative:,}")
    print(f"  With Duplicates:   {years_with_duplicates:,}")
    
    # Find specific examples
    print("\n" + "="*60)
    print("VERIFICATION EXAMPLES")
    print("="*60)
    
    for assoc in processed_data:
        name = assoc['name']
        if 'PHILHARMONIE' in name.upper():
            print(f"\n{name}:")
            print(f"  Raw Total: {assoc.get('totalAmount', 0):,.0f} €")
            print(f"  Net Total: {assoc['netTotalAmount']:,.0f} €")
            for ns in assoc['netSubventions']:
                print(f"    {ns['year']}: {ns['net_amount']:>15,.0f} € net (was {ns['raw_amount']:>15,.0f} € raw)")
        
        if 'MUSICAL DE PARIS' in name.upper():
            print(f"\n{name}:")
            print(f"  Raw Total: {assoc.get('totalAmount', 0):,.0f} €")
            print(f"  Net Total: {assoc['netTotalAmount']:,.0f} €")
            for ns in assoc['netSubventions']:
                print(f"    {ns['year']}: {ns['net_amount']:>15,.0f} € net (was {ns['raw_amount']:>15,.0f} € raw)")
    
    print("\n" + "="*60)
    print(f"Output saved to: data_net.json")
    print("="*60)


if __name__ == '__main__':
    main()
