"use client";

import { useState } from "react";
import type { ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import type {
  ApprovedUseStatus,
  CookingIntensity,
  FloorPosition,
  LayoutShape,
  Readiness,
} from "@/services/intakeTransfer";

export interface IntakeFormValues {
  businessType: string;
  expectedRent: string;
  squareMeters: string;
  leaseTermMonths: string;
  serviceChargeMonthly: string;
  fitoutBudget: string;
  cookingIntensity: CookingIntensity;
  floorPosition: FloorPosition;
  layoutShape: LayoutShape;
  hasWaterSupply: Readiness;
  hasFloorTrap: Readiness;
  hasGreaseTrap: Readiness;
  electricalReadiness: Readiness;
  hasGas: Readiness;
  hasExhaust: Readiness;
  wastewaterReadiness: Readiness;
  approvedUseStatus: ApprovedUseStatus;
  rentFreeMonths: string;
  depositMonths: string;
  otherMonthlyCosts: string;
  utilitiesMonthlyEstimate: string;
  staffingMonthly: string;
  marketingMonthly: string;
  insuranceMonthly: string;
  licenseFees: string;
  reinstatementCost: string;
  expectedDailyCustomers: string;
  averageSpend: string;
  grossMargin: string;
  frontageWidthM: string;
  ceilingHeightM: string;
  usableAreaRatio: string;
  storageAreaSqm: string;
  seatingCapacity: string;
  loadingAccess: Readiness;
  toiletAccess: Readiness;
  signageVisibility: Readiness;
  exhaustRouteAvailable: Readiness;
}

export const DEFAULT_INTAKE_FORM_VALUES: IntakeFormValues = {
  businessType: "",
  expectedRent: "",
  squareMeters: "",
  leaseTermMonths: "36",
  serviceChargeMonthly: "0",
  fitoutBudget: "60000",
  cookingIntensity: "light",
  floorPosition: "ground",
  layoutShape: "regular",
  hasWaterSupply: "unknown",
  hasFloorTrap: "unknown",
  hasGreaseTrap: "unknown",
  electricalReadiness: "unknown",
  hasGas: "unknown",
  hasExhaust: "unknown",
  wastewaterReadiness: "unknown",
  approvedUseStatus: "unknown",
  rentFreeMonths: "",
  depositMonths: "",
  otherMonthlyCosts: "",
  utilitiesMonthlyEstimate: "",
  staffingMonthly: "",
  marketingMonthly: "",
  insuranceMonthly: "",
  licenseFees: "",
  reinstatementCost: "",
  expectedDailyCustomers: "",
  averageSpend: "",
  grossMargin: "",
  frontageWidthM: "",
  ceilingHeightM: "",
  usableAreaRatio: "",
  storageAreaSqm: "",
  seatingCapacity: "",
  loadingAccess: "unknown",
  toiletAccess: "unknown",
  signageVisibility: "unknown",
  exhaustRouteAvailable: "unknown",
};

interface IntakeFormProps {
  values: IntakeFormValues;
  onChange: <K extends keyof IntakeFormValues>(
    key: K,
    value: IntakeFormValues[K]
  ) => void;
}

export function IntakeForm({ values, onChange }: IntakeFormProps) {
  const [advancedOpen, setAdvancedOpen] = useState(false);

  return (
    <div className="space-y-4">
      <section className="space-y-3">
        <SectionLabel>Basic</SectionLabel>
        <div className="grid grid-cols-3 gap-3">
          <TextField
            label="Industry"
            placeholder="Cafe, bakery, boutique"
            value={values.businessType}
            onChange={(value) => onChange("businessType", value)}
          />
          <NumberField
            label="Monthly Rent"
            placeholder="5000"
            value={values.expectedRent}
            onChange={(value) => onChange("expectedRent", value)}
          />
          <NumberField
            label="Shop Size"
            placeholder="80"
            value={values.squareMeters}
            onChange={(value) => onChange("squareMeters", value)}
          />
          <NumberField
            label="Lease Term"
            placeholder="36"
            value={values.leaseTermMonths}
            onChange={(value) => onChange("leaseTermMonths", value)}
          />
          <NumberField
            label="Service Charge"
            placeholder="0"
            value={values.serviceChargeMonthly}
            onChange={(value) => onChange("serviceChargeMonthly", value)}
          />
          <NumberField
            label="Fit-out Budget"
            placeholder="60000"
            value={values.fitoutBudget}
            onChange={(value) => onChange("fitoutBudget", value)}
          />
        </div>
      </section>

      <section className="space-y-3 border border-zinc-800 p-4">
        <SectionLabel>F&B Readiness</SectionLabel>
        <div className="grid grid-cols-3 gap-3">
          <Segmented
            label="Cooking"
            value={values.cookingIntensity}
            options={[
              ["none", "None"],
              ["light", "Light"],
              ["full", "Full"],
            ]}
            onChange={(value) => onChange("cookingIntensity", value)}
          />
          <SelectField
            label="Floor"
            value={values.floorPosition}
            options={[
              ["basement", "Basement"],
              ["ground", "Ground"],
              ["upper", "Upper"],
              ["mall", "Mall"],
              ["unknown", "Unknown"],
            ]}
            onChange={(value) => onChange("floorPosition", value)}
          />
          <SelectField
            label="Layout"
            value={values.layoutShape}
            options={[
              ["regular", "Regular"],
              ["narrow", "Narrow"],
              ["corner", "Corner"],
              ["irregular", "Irregular"],
              ["unknown", "Unknown"],
            ]}
            onChange={(value) => onChange("layoutShape", value)}
          />
        </div>

        <div className="grid grid-cols-2 gap-2">
          <ReadinessRow
            label="Water"
            value={values.hasWaterSupply}
            onChange={(value) => onChange("hasWaterSupply", value)}
          />
          <ReadinessRow
            label="Power"
            value={values.electricalReadiness}
            onChange={(value) => onChange("electricalReadiness", value)}
          />
          <ReadinessRow
            label="Gas"
            value={values.hasGas}
            onChange={(value) => onChange("hasGas", value)}
          />
          <ReadinessRow
            label="Floor Trap"
            value={values.hasFloorTrap}
            onChange={(value) => onChange("hasFloorTrap", value)}
          />
          <ReadinessRow
            label="Grease Trap"
            value={values.hasGreaseTrap}
            onChange={(value) => onChange("hasGreaseTrap", value)}
          />
          <ReadinessRow
            label="Exhaust"
            value={values.hasExhaust}
            onChange={(value) => onChange("hasExhaust", value)}
          />
          <ReadinessRow
            label="Wastewater"
            value={values.wastewaterReadiness}
            onChange={(value) => onChange("wastewaterReadiness", value)}
          />
          <Segmented
            label="Approved Use"
            value={values.approvedUseStatus}
            options={[
              ["confirmed", "OK"],
              ["unknown", "?"],
              ["needs_change_of_use", "Change"],
            ]}
            onChange={(value) => onChange("approvedUseStatus", value)}
          />
        </div>
      </section>

      <section className="border border-zinc-800">
        <button
          type="button"
          onClick={() => setAdvancedOpen((open) => !open)}
          className="flex w-full items-center justify-between px-4 py-3 font-mono text-[10px] uppercase tracking-[0.18em] text-zinc-500"
        >
          Advanced assumptions
          <ChevronDown
            size={14}
            className={cn("transition-transform", advancedOpen && "rotate-180")}
          />
        </button>
        {advancedOpen && (
          <div className="grid grid-cols-3 gap-3 border-t border-zinc-800 p-4">
            <NumberField
              label="Rent-free"
              placeholder="2"
              value={values.rentFreeMonths}
              onChange={(value) => onChange("rentFreeMonths", value)}
            />
            <NumberField
              label="Deposit"
              placeholder="3"
              value={values.depositMonths}
              onChange={(value) => onChange("depositMonths", value)}
            />
            <NumberField
              label="Other Costs"
              placeholder="1200"
              value={values.otherMonthlyCosts}
              onChange={(value) => onChange("otherMonthlyCosts", value)}
            />
            <NumberField
              label="Utilities"
              placeholder="900"
              value={values.utilitiesMonthlyEstimate}
              onChange={(value) => onChange("utilitiesMonthlyEstimate", value)}
            />
            <NumberField
              label="Staffing"
              placeholder="12000"
              value={values.staffingMonthly}
              onChange={(value) => onChange("staffingMonthly", value)}
            />
            <NumberField
              label="Marketing"
              placeholder="700"
              value={values.marketingMonthly}
              onChange={(value) => onChange("marketingMonthly", value)}
            />
            <NumberField
              label="Insurance"
              placeholder="250"
              value={values.insuranceMonthly}
              onChange={(value) => onChange("insuranceMonthly", value)}
            />
            <NumberField
              label="Licence Fees"
              placeholder="900"
              value={values.licenseFees}
              onChange={(value) => onChange("licenseFees", value)}
            />
            <NumberField
              label="Reinstatement"
              placeholder="15000"
              value={values.reinstatementCost}
              onChange={(value) => onChange("reinstatementCost", value)}
            />
            <NumberField
              label="Daily Customers"
              placeholder="140"
              value={values.expectedDailyCustomers}
              onChange={(value) => onChange("expectedDailyCustomers", value)}
            />
            <NumberField
              label="Average Spend"
              placeholder="18"
              value={values.averageSpend}
              onChange={(value) => onChange("averageSpend", value)}
            />
            <NumberField
              label="Gross Margin"
              placeholder="0.68"
              value={values.grossMargin}
              step="0.01"
              onChange={(value) => onChange("grossMargin", value)}
            />
            <NumberField
              label="Frontage"
              placeholder="6"
              value={values.frontageWidthM}
              step="0.1"
              onChange={(value) => onChange("frontageWidthM", value)}
            />
            <NumberField
              label="Ceiling"
              placeholder="3.2"
              value={values.ceilingHeightM}
              step="0.1"
              onChange={(value) => onChange("ceilingHeightM", value)}
            />
            <NumberField
              label="Usable Ratio"
              placeholder="0.78"
              value={values.usableAreaRatio}
              step="0.01"
              onChange={(value) => onChange("usableAreaRatio", value)}
            />
            <NumberField
              label="Storage"
              placeholder="8"
              value={values.storageAreaSqm}
              onChange={(value) => onChange("storageAreaSqm", value)}
            />
            <NumberField
              label="Seats"
              placeholder="32"
              value={values.seatingCapacity}
              onChange={(value) => onChange("seatingCapacity", value)}
            />
            <ReadinessRow
              label="Loading"
              value={values.loadingAccess}
              onChange={(value) => onChange("loadingAccess", value)}
            />
            <ReadinessRow
              label="Toilet"
              value={values.toiletAccess}
              onChange={(value) => onChange("toiletAccess", value)}
            />
            <ReadinessRow
              label="Signage"
              value={values.signageVisibility}
              onChange={(value) => onChange("signageVisibility", value)}
            />
            <ReadinessRow
              label="Exhaust Route"
              value={values.exhaustRouteAvailable}
              onChange={(value) => onChange("exhaustRouteAvailable", value)}
            />
          </div>
        )}
      </section>
    </div>
  );
}

function SectionLabel({ children }: { children: string }) {
  return (
    <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-zinc-500">
      {children}
    </div>
  );
}

interface TextFieldProps {
  label: string;
  value: string;
  placeholder: string;
  onChange: (value: string) => void;
}

function TextField({ label, value, placeholder, onChange }: TextFieldProps) {
  return (
    <FieldShell label={label}>
      <input
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className={inputClassName}
      />
    </FieldShell>
  );
}

interface NumberFieldProps extends TextFieldProps {
  step?: string;
}

function NumberField({ label, value, placeholder, step, onChange }: NumberFieldProps) {
  return (
    <FieldShell label={label}>
      <input
        type="number"
        min="0"
        step={step}
        placeholder={placeholder}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className={inputClassName}
      />
    </FieldShell>
  );
}

interface SelectFieldProps<T extends string> {
  label: string;
  value: T;
  options: Array<[T, string]>;
  onChange: (value: T) => void;
}

function SelectField<T extends string>({
  label,
  value,
  options,
  onChange,
}: SelectFieldProps<T>) {
  return (
    <FieldShell label={label}>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value as T)}
        className={inputClassName}
      >
        {options.map(([optionValue, text]) => (
          <option key={optionValue} value={optionValue}>
            {text}
          </option>
        ))}
      </select>
    </FieldShell>
  );
}

function FieldShell({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <label className="space-y-2">
      <span className="block font-mono text-[10px] uppercase tracking-[0.14em] text-zinc-500">
        {label}
      </span>
      {children}
    </label>
  );
}

const inputClassName = cn(
  "w-full rounded border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm",
  "font-mono text-zinc-100 placeholder:text-zinc-600",
  "focus:border-zinc-600 focus:outline-none"
);

interface SegmentedProps<T extends string> {
  label: string;
  value: T;
  options: Array<[T, string]>;
  onChange: (value: T) => void;
}

function Segmented<T extends string>({
  label,
  value,
  options,
  onChange,
}: SegmentedProps<T>) {
  return (
    <div className="space-y-2">
      <span className="block font-mono text-[10px] uppercase tracking-[0.14em] text-zinc-500">
        {label}
      </span>
      <div className="grid grid-cols-[repeat(auto-fit,minmax(0,1fr))] border border-zinc-800">
        {options.map(([optionValue, text]) => (
          <button
            key={optionValue}
            type="button"
            onClick={() => onChange(optionValue)}
            className={cn(
              "min-w-0 border-r border-zinc-800 px-2 py-2 font-mono text-[10px]",
              "uppercase text-zinc-500 last:border-r-0 hover:text-zinc-200",
              value === optionValue && "bg-lime-300/10 text-lime-200"
            )}
          >
            {text}
          </button>
        ))}
      </div>
    </div>
  );
}

function ReadinessRow({
  label,
  value,
  onChange,
}: {
  label: string;
  value: Readiness;
  onChange: (value: Readiness) => void;
}) {
  return (
    <Segmented
      label={label}
      value={value}
      options={[
        ["yes", "Yes"],
        ["unknown", "?"],
        ["no", "No"],
      ]}
      onChange={onChange}
    />
  );
}
