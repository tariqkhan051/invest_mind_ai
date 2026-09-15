import { useEffect, useMemo, useState, type FormEvent } from "react";

import { createTransaction } from "../api/client";
import type { Asset, CreateTransactionPayload, TransactionType } from "../types/api";
import { formatCurrency } from "../utils/format";

export type InputMode =
  | "cash_deposit"
  | "buy"
  | "sell"
  | "switch"
  | "sip";

interface TransactionFormProps {
  assets: Asset[];
  defaultMode?: InputMode;
  prefills?: Partial<{
    mode: InputMode;
    assetId: string;
    fromAssetId: string;
    toAssetId: string;
    amount: string;
    units: string;
    price: string;
    notes: string;
  }>;
  onCreated: () => Promise<void> | void;
}

const MODE_OPTIONS: Array<{ id: InputMode; label: string }> = [
  { id: "cash_deposit", label: "Add Cash" },
  { id: "buy", label: "Buy" },
  { id: "sell", label: "Sell" },
  { id: "switch", label: "Switch / Move" },
  { id: "sip", label: "SIP / Monthly" },
];

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export function TransactionForm({
  assets,
  defaultMode = "buy",
  prefills,
  onCreated,
}: TransactionFormProps) {
  const [mode, setMode] = useState<InputMode>(prefills?.mode ?? defaultMode);
  const [assetId, setAssetId] = useState(prefills?.assetId ?? "");
  const [fromAssetId, setFromAssetId] = useState(prefills?.fromAssetId ?? "");
  const [toAssetId, setToAssetId] = useState(prefills?.toAssetId ?? "");
  const [amount, setAmount] = useState(prefills?.amount ?? "");
  const [units, setUnits] = useState(prefills?.units ?? "");
  const [price, setPrice] = useState(prefills?.price ?? "");
  const [notes, setNotes] = useState(prefills?.notes ?? "");
  const [transactionDate, setTransactionDate] = useState(todayIso());
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!prefills) return;
    if (prefills.mode) setMode(prefills.mode);
    if (prefills.assetId) setAssetId(prefills.assetId);
    if (prefills.fromAssetId) setFromAssetId(prefills.fromAssetId);
    if (prefills.toAssetId) setToAssetId(prefills.toAssetId);
    if (prefills.amount !== undefined) setAmount(prefills.amount);
    if (prefills.units !== undefined) setUnits(prefills.units);
    if (prefills.price !== undefined) setPrice(prefills.price);
    if (prefills.notes !== undefined) setNotes(prefills.notes);
  }, [prefills]);

  const sortedAssets = useMemo(
    () =>
      [...assets].sort((a, b) => a.symbol.localeCompare(b.symbol)),
    [assets],
  );

  const fallbackAssetId = sortedAssets[0]?.id ?? "";

  const estimate = useMemo(() => {
    const u = Number(units);
    const p = Number(price);
    if (!Number.isFinite(u) || !Number.isFinite(p) || u <= 0 || p <= 0) {
      return null;
    }
    return u * p;
  }, [units, price]);

  const submitOne = async (payload: CreateTransactionPayload) => {
    await createTransaction(payload);
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    setMessage(null);

    try {
      if (mode === "cash_deposit") {
        const gross = Number(amount);
        if (!Number.isFinite(gross) || gross <= 0) {
          throw new Error("Enter a valid cash amount.");
        }
        await submitOne({
          asset_id: assetId || fallbackAssetId,
          transaction_type: "adjustment",
          units: 0,
          price: 0,
          gross_amount: gross,
          transaction_date: transactionDate,
          notes: notes || "Cash deposit",
          source: "manual",
        });
        setMessage(`Cash deposit of ${formatCurrency(gross)} recorded.`);
      } else if (mode === "switch") {
        const moveAmount = Number(amount);
        const unitPrice = Number(price);
        if (!fromAssetId || !toAssetId) {
          throw new Error("Select both source and destination assets.");
        }
        if (!Number.isFinite(moveAmount) || moveAmount <= 0) {
          throw new Error("Enter a valid switch amount.");
        }
        if (!Number.isFinite(unitPrice) || unitPrice <= 0) {
          throw new Error("Enter a valid price/NAV for unit conversion.");
        }
        const switchUnits = Number((moveAmount / unitPrice).toFixed(6));
        await submitOne({
          asset_id: fromAssetId,
          transaction_type: "switch_out",
          units: switchUnits,
          price: unitPrice,
          transaction_date: transactionDate,
          notes: notes || `Switch out toward destination`,
          source: "manual",
        });
        await submitOne({
          asset_id: toAssetId,
          transaction_type: "switch_in",
          units: switchUnits,
          price: unitPrice,
          transaction_date: transactionDate,
          notes: notes || `Switch in from source`,
          source: "manual",
        });
        setMessage(
          `Moved about ${formatCurrency(moveAmount)} via switch (${switchUnits} units).`,
        );
      } else {
        const selectedAsset = assetId || fallbackAssetId;
        if (!selectedAsset) {
          throw new Error("Select an asset first.");
        }
        const unitValue = Number(units);
        const priceValue = Number(price);
        const amountValue = Number(amount);

        let finalUnits = unitValue;
        let finalPrice = priceValue;

        if ((!Number.isFinite(finalUnits) || finalUnits <= 0) && amountValue > 0 && priceValue > 0) {
          finalUnits = Number((amountValue / priceValue).toFixed(6));
        }
        if ((!Number.isFinite(finalPrice) || finalPrice <= 0) && amountValue > 0 && unitValue > 0) {
          finalPrice = Number((amountValue / unitValue).toFixed(6));
        }

        if (!Number.isFinite(finalUnits) || finalUnits <= 0) {
          throw new Error("Enter units (or amount + price).");
        }
        if (!Number.isFinite(finalPrice) || finalPrice <= 0) {
          throw new Error("Enter a valid price/NAV.");
        }

        let transactionType: TransactionType = "buy";
        if (mode === "sell") transactionType = "sell";
        if (mode === "sip") transactionType = "automatic_sip";

        await submitOne({
          asset_id: selectedAsset,
          transaction_type: transactionType,
          units: finalUnits,
          price: finalPrice,
          transaction_date: transactionDate,
          notes: notes || undefined,
          source: "manual",
        });
        setMessage(
          `${transactionType.replace("_", " ")} recorded for ${finalUnits} units.`,
        );
      }

      setAmount("");
      setUnits("");
      setPrice("");
      setNotes("");
      await onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save transaction");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="input-form" onSubmit={(event) => void handleSubmit(event)}>
      <div className="mode-tabs">
        {MODE_OPTIONS.map((option) => (
          <button
            key={option.id}
            type="button"
            className={mode === option.id ? "mode-tab active" : "mode-tab"}
            onClick={() => setMode(option.id)}
          >
            {option.label}
          </button>
        ))}
      </div>

      <div className="form-grid">
        {mode === "switch" ? (
          <>
            <label>
              From asset
              <select
                value={fromAssetId}
                onChange={(event) => setFromAssetId(event.target.value)}
                required
              >
                <option value="">Select source</option>
                {sortedAssets.map((asset) => (
                  <option key={asset.id} value={asset.id}>
                    {asset.symbol} · {asset.display_name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              To asset
              <select
                value={toAssetId}
                onChange={(event) => setToAssetId(event.target.value)}
                required
              >
                <option value="">Select destination</option>
                {sortedAssets.map((asset) => (
                  <option key={asset.id} value={asset.id}>
                    {asset.symbol} · {asset.display_name}
                  </option>
                ))}
              </select>
            </label>
          </>
        ) : (
          <label>
            {mode === "cash_deposit" ? "Reference asset" : "Asset"}
            <select
              value={assetId || fallbackAssetId}
              onChange={(event) => setAssetId(event.target.value)}
              required
            >
              <option value="">Select asset</option>
              {sortedAssets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.symbol} · {asset.display_name}
                </option>
              ))}
            </select>
          </label>
        )}

        {mode === "cash_deposit" || mode === "switch" ? (
          <label>
            Amount (PKR)
            <input
              type="number"
              min="0"
              step="0.01"
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              required
            />
          </label>
        ) : null}

        {mode !== "cash_deposit" ? (
          <>
            {mode !== "switch" ? (
              <label>
                Amount (PKR, optional)
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={amount}
                  onChange={(event) => setAmount(event.target.value)}
                  placeholder="Used with price to compute units"
                />
              </label>
            ) : null}
            <label>
              Units
              <input
                type="number"
                min="0"
                step="0.0001"
                value={units}
                onChange={(event) => setUnits(event.target.value)}
                placeholder={mode === "switch" ? "Auto from amount ÷ price" : ""}
                required={mode !== "switch" && !amount}
              />
            </label>
            <label>
              Price / NAV
              <input
                type="number"
                min="0"
                step="0.0001"
                value={price}
                onChange={(event) => setPrice(event.target.value)}
                required
              />
            </label>
          </>
        ) : null}

        <label>
          Date
          <input
            type="date"
            value={transactionDate}
            onChange={(event) => setTransactionDate(event.target.value)}
            required
          />
        </label>

        <label className="full-width">
          Notes
          <input
            type="text"
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            placeholder="Optional note for history"
          />
        </label>
      </div>

      {estimate !== null && mode !== "cash_deposit" ? (
        <p className="section-hint">Estimated trade value: {formatCurrency(estimate)}</p>
      ) : null}

      {error ? <p className="page-state error">{error}</p> : null}
      {message ? <p className="form-success">{message}</p> : null}

      <div className="action-row">
        <button type="submit" className="primary-button" disabled={submitting || assets.length === 0}>
          {submitting ? "Saving..." : "Save transaction"}
        </button>
      </div>
    </form>
  );
}
